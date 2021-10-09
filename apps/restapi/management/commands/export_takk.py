# from django.core.management.base import BaseCommand
# from import_export import resources
# from apps.modifiers import models as modifier_models
# from apps.orders import models as order_models
# from apps.payment import models as payment_models
# from apps.products import models as product_models
# from apps.users import models as user_models
#
#
# # Modifiers
# class ModifierCategory(resources.ModelResource):
#     class Meta:
#         model = modifier_models.ModifierCategory
#
#
# class Modifier(resources.ModelResource):
#     class Meta:
#         model = modifier_models.Modifier
#
#
# # Order
# class Message(resources.ModelResource):
#     class Meta:
#         model = order_models.Message
#
#
# class MessageItem(resources.ModelResource):
#     class Meta:
#         model = order_models.MessageItem
#
#
# class Delivery(resources.ModelResource):
#     class Meta:
#         model = order_models.Delivery
#
#
# class Order(resources.ModelResource):
#     class Meta:
#         model = order_models.Order
#
#
# class Cart(resources.ModelResource):
#     class Meta:
#         model = order_models.Cart
#
#
# class CartModifier(resources.ModelResource):
#     class Meta:
#         model = order_models.CartModifier
#
#
# class FavoriteCartItem(resources.ModelResource):
#     class Meta:
#         model = order_models.FavoriteCartItem
#
#
# class FavoriteCart(resources.ModelResource):
#     class Meta:
#         model = order_models.FavoriteCart
#
#
# class Transaction(resources.ModelResource):
#     class Meta:
#         model = order_models.Transaction
#
#
# #  Payment
#
#
# class StripeTransaction(resources.ModelResource):
#     class Meta:
#         model = payment_models.StripeTransaction
#
#
# class PaypalTransaction(resources.ModelResource):
#     class Meta:
#         model = payment_models.PaypalTransaction
#
#
# # Product
#
#
# class CafeMenu(resources.ModelResource):
#     class Meta:
#         model = product_models.CafeMenu
#
#
# class ProductCategory(resources.ModelResource):
#     class Meta:
#         model = product_models.ProductCategory
#
#
# class ProductImage(resources.ModelResource):
#     class Meta:
#         model = product_models.ProductImage
#
#
# class Product(resources.ModelResource):
#     class Meta:
#         model = product_models.Product
#
#
# class ProductSize(resources.ModelResource):
#     class Meta:
#         model = product_models.ProductSize
#
#
# class Size(resources.ModelResource):
#     class Meta:
#         model = product_models.Size
#
#
# class CafeMeals(resources.ModelResource):
#     class Meta:
#         model = product_models.CafeMeals
#
#
# class ProductModifier(resources.ModelResource):
#     class Meta:
#         model = product_models.ProductModifier
#
#
# class ProductProfile(resources.ModelResource):
#     class Meta:
#         model = product_models.ProductProfile
#
#
# # User
#
#
# class Album(resources.ModelResource):
#     class Meta:
#         model = user_models.Album
#
#
# class File(resources.ModelResource):
#     class Meta:
#         model = user_models.File
#
#
# class User(resources.ModelResource):
#     class Meta:
#         model = user_models.User
#
#
# class Budget(resources.ModelResource):
#     class Meta:
#         model = user_models.Budget
#
#
# class SocialProfile(resources.ModelResource):
#     class Meta:
#         model = user_models.SocialProfile
#
#
# class Category(resources.ModelResource):
#     class Meta:
#         model = user_models.Category
#
#
# class WeekTime(resources.ModelResource):
#     class Meta:
#         model = user_models.WeekTime
#
#
# class Cafe(resources.ModelResource):
#     class Meta:
#         model = user_models.Cafe
#
#
# class Company(resources.ModelResource):
#     class Meta:
#         model = user_models.Company
#
#
# class CafeGeneralSettings(resources.ModelResource):
#     class Meta:
#         model = user_models.CafeGeneralSettings
#
#
# class Cashier(resources.ModelResource):
#     class Meta:
#         model = user_models.Cashier
#
#
# class Employee(resources.ModelResource):
#     class Meta:
#         model = user_models.Employee
#
#
# class Point(resources.ModelResource):
#     class Meta:
#         model = user_models.Point
#
#
# class FreeItem(resources.ModelResource):
#     class Meta:
#         model = user_models.FreeItem
#
#
# class AdditionalPercent(resources.ModelResource):
#     class Meta:
#         model = user_models.FreeItem
#
#
# class Cashback(resources.ModelResource):
#     class Meta:
#         model = user_models.FreeItem
#
#
# class Command(BaseCommand):
#
#     def handle(self, *args, **options):
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod_item = Modifier().export().xlsx
#         self.save_file(mod_item, 'modifier')
#
#         order_message = Message().export().xlsx
#         self.save_file(order_message, 'order message')
#
#         order_message_item = MessageItem().export().xlsx
#         self.save_file(order_message_item, 'order message item')
#
#         delivery = Delivery().export().xlsx
#         self.save_file(delivery, 'delivery')
#
#         order = Order().export().xlsx
#         self.save_file(order, 'order')
#
#         cart = Cart().export().xlsx
#         self.save_file(cart, 'cart')
#
#         cart_modifier = CartModifier().export().xlsx
#         self.save_file(cart_modifier, 'cart modifier')
#
#         favorite_cart_item = FavoriteCartItem().export().xlsx
#         self.save_file(favorite_cart_item, 'favorite cart item')
#
#         favorite_cart = FavoriteCart().export().xlsx
#         self.save_file(favorite_cart, 'favorite cart')
#
#         transaction = Transaction().export().xlsx
#         self.save_file(transaction, 'transaction')
#
#         stripe_transaction = StripeTransaction().export().xlsx
#         self.save_file(stripe_transaction, 'stripe transaction')
#
#         paypal_transaction = PaypalTransaction().export().xlsx
#         self.save_file(paypal_transaction, 'paypal transaction')
#
#         cafe_menu = CafeMenu().export().xlsx
#         self.save_file(cafe_menu, 'cafe_menu')
#
#         product_category = ProductCategory().export().xlsx
#         self.save_file(product_category, 'product category')
#
#         product_image = ProductImage().export().xlsx
#         self.save_file(product_image, 'product image')
#
#         product = Product().export().xlsx
#         self.save_file(product, 'product')
#
#         product_size = ProductSize().export().xlsx
#         self.save_file(product_size, 'product_size')
#
#         size = Size().export().xlsx
#         self.save_file(size, 'size')
#
#         cafe_meals = CafeMeals().export().xlsx
#         self.save_file(cafe_meals, 'cafe meals')
#
#         product_modifier = ProductModifier().export().xlsx
#         self.save_file(product_modifier, 'product modifier')
#
#         product_profile = ProductProfile().export().xlsx
#         self.save_file(product_profile, 'product profile')
#
#         album = Album().export().xlsx
#         self.save_file(album, 'album')
#
#         file = File().export().xlsx
#         self.save_file(file, 'file')
#
#         user = User().export().xlsx
#         self.save_file(user, 'user')
#
#         budget = Budget().export().xlsx
#         self.save_file(budget, 'budget')
#
#         category = Category().export().xlsx
#         self.save_file(category, 'cafe category')
#
#         week_time = WeekTime().export().xlsx
#         self.save_file(week_time, 'week time')
#
#         cafe = Cafe().export().xlsx
#         self.save_file(cafe, 'cafe')
#
#         company = Company().export().xlsx
#         self.save_file(company, 'company')
#
#         cafe_general_settings = CafeGeneralSettings().export().xlsx
#         self.save_file(cafe_general_settings, 'cafe general settings')
#
#         cashier = Cashier().export().xlsx
#         self.save_file(cashier, 'cashier')
#
#         employee = Employee().export().xlsx
#         self.save_file(employee, 'employee')
#
#         point = Point().export().xlsx
#         self.save_file(point, 'point')
#
#         free_item = FreeItem().export().xlsx
#         self.save_file(free_item, 'free_item')
#
#         additional_percent = AdditionalPercent().export().xlsx
#         self.save_file(additional_percent, 'additional percent')
#
#         cashback = Cashback().export().xlsx
#         self.save_file(cashback, 'cashback')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#         mod = ModifierCategory().export().xlsx
#         self.save_file(mod, 'modifier category')
#
#     @staticmethod
#     def save_file(x, name):
#         with open('{}.xlsx'.format(name), 'wb') as save_user:
#             save_user.write(x)
#
#
#
