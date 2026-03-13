from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from django.utils import timezone
from .models import StockItem, StockMovement


# ══════════════════════════════════════════════════════════
# FILTRES PERSONNALISÉS
# ══════════════════════════════════════════════════════════

class StockLevelFilter(admin.SimpleListFilter):
    title        = 'Niveau stock'
    parameter_name = 'stock_level'

    def lookups(self, request, model_admin):
        return [
            ('out',      '🔴 Rupture (0)'),
            ('critical', '🟠 Critique (≤ min)'),
            ('ok',       '🟢 OK'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'out':
            return queryset.filter(quantity=0)
        if self.value() == 'critical':
            return queryset.filter(quantity__gt=0, quantity__lte=F('min_quantity'))
        if self.value() == 'ok':
            return queryset.filter(quantity__gt=F('min_quantity'))
        return queryset


# ══════════════════════════════════════════════════════════
# INLINE — Mouvements dans la fiche article
# ══════════════════════════════════════════════════════════

class StockMovementInline(admin.TabularInline):
    model           = StockMovement
    extra           = 0
    max_num         = 10          # affiche les 10 derniers
    can_delete      = False
    readonly_fields = ['movement_type', 'quantity_display', 'reason',
                       'done_by', 'ticket', 'reference_doc', 'created_at']
    fields          = readonly_fields
    ordering        = ['-created_at']

    def quantity_display(self, obj):
        color = '#2ecc71' if obj.quantity > 0 else '#e74c3c'
        sign  = '+' if obj.quantity > 0 else ''
        return format_html(
            '<span style="color:{};font-weight:bold">{}{}</span>',
            color, sign, obj.quantity
        )
    quantity_display.short_description = 'Qté'

    def has_add_permission(self, request, obj=None):
        return False


# ══════════════════════════════════════════════════════════
# ACTIONS ADMIN
# ══════════════════════════════════════════════════════════

@admin.action(description='📦 Réapprovisionner — remettre au seuil minimum x2')
def restock_to_minimum(modeladmin, request, queryset):
    for item in queryset.filter(quantity__lte=F('min_quantity')):
        needed = (item.min_quantity * 2) - item.quantity
        if needed > 0:
            StockMovement.objects.create(
                item=item,
                movement_type='in',
                quantity=needed,
                reason='Réapprovisionnement auto admin',
                done_by=request.user.username,
            )
    modeladmin.message_user(request, "Réapprovisionnement effectué.")


@admin.action(description='📋 Exporter sélection (affichage quantités)')
def export_with_quantities(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom', 'Référence', 'Type', 'Marque',
                     'Qté en stock', 'Seuil min', 'Prix unitaire',
                     'Valeur totale', 'Dernière MAJ'])

    for item in queryset:
        writer.writerow([
            item.id, item.name, item.reference, item.item_type,
            item.brand.name if item.brand else '',
            item.quantity, item.min_quantity, item.unit_price,
            item.total_value, timezone.localtime(item.updated_at).strftime('%Y-%m-%d %H:%M'),
        ])

    return response
