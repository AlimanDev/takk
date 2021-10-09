from django.core.management.base import BaseCommand
from apps.companies import models as company_models
from apps.products import models as product_models


class Command(BaseCommand):

    def handle(self, *args, **options):
        menu = company_models.Menu.objects.get(pk=1)
        del_menu = company_models.Menu.objects.exclude(pk=1)
        del_menu.delete()
        self.duplicate_menu(menu)

    def duplicate_menu(self, menu):

        new_menu = company_models.Menu.objects.create(
            company=menu.company,
            name='{} duplicate'.format(menu.name)
        )

        categories = menu.categories.all()
        modifiers = menu.modifiers.all()

        for modifier in modifiers:

            new_modifier = product_models.Modifier.objects.get(pk=modifier.pk)
            new_modifier.menu = new_menu
            new_modifier.pk = None
            new_modifier.save()

            for item in modifier.items.all():
                new_item = item
                new_item.modifier = new_modifier
                new_item.pk = None
                new_item.save()
        new_modifiers = new_menu.modifiers.all()

        for category in categories:

            if not category.parent:
                new_category = product_models.ProductCategory.objects.get(pk=category.pk)
                new_category.menu = new_menu
                new_category.pk = None
                new_category.save(force_insert=True)


                for sub_category in category.children.all():
                    new_sub_category = product_models.ProductCategory.objects.get(pk=sub_category.pk)
                    new_sub_category.parent = new_category
                    new_sub_category.pk = None
                    new_sub_category.save(force_insert=True)


                    for product in sub_category.products.all():
                        new_product = product_models.Product.objects.get(pk=product.pk)
                        new_product.category = new_sub_category
                        new_product.pk = product_models.Product.objects.first().pk + 1
                        # new_product.modifiers.clear()
                        new_product.save(force_insert=True)

                        for size in product.sizes.all():
                            new_size = product_models.ProductSize.objects.get(pk=size.pk)
                            new_size.product = new_product
                            new_size.pk = product_models.ProductSize.objects.first().pk + 1
                            new_size.save(force_insert=True)

                        if product.modifiers.all():
                            for modifier in product.modifiers.all():
                                mod = new_modifiers.filter(name=modifier.name).first()
                                new_product.modifiers.add(mod)



                if category.products.all():

                    for product in category.products.all():
                        new_product = product_models.Product.objects.get(pk=product.pk)
                        new_product.category = new_category
                        new_product.pk = product_models.Product.objects.first().pk + 1
                        # new_product.modifiers.clear()
                        new_product.save(force_insert=True)

                        for size in product.sizes.all():
                            new_size = product_models.ProductSize.objects.get(pk=size.pk)
                            new_size.product = new_product
                            new_size.pk = product_models.ProductSize.objects.first().pk + 1
                            new_size.save(force_insert=True)

                        if product.modifiers.all():
                            for modifier in product.modifiers.all():
                                mod = new_modifiers.filter(name=modifier.name).first()
                                new_product.modifiers.add(mod)








