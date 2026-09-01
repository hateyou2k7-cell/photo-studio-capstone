from database.databases.factory_database import FactoryDatabase
# from database.databases.mssql import init_mssql
# from database.databases.postgres import init_postgres
from database.models import course_model
from database.models import room_model
from database.models import space_management_model
from database.models.auth import auth_user_model, auth_role_model,auth_funtion_model
from database.models.sell import sell_customer_model, sell_product_model, sell_invoice_model
from database.models.pay import pay_tran_model
from database.models import equipment_model, package_booking_model
from database.models import (User, ProviderProfile, Space, Resource, SpaceResource, Consumable,
                                   ServicePackage, PackageItem, Reservation, ReservationItem, Payment,
                                   ServiceSession, Review, Post, Comment, Workshop, WorkshopRegistration,
                                   Conversation, Message)

def init_db(app):
    # init_mssql(app)
    FactoryDatabase.get_database('POSTGREE').init_database(app)
    # init_postgres(app)
    
# Migration Entities -> tables
from database.databases.mssql import Base