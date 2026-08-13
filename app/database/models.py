from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, ForeignKey, 
    Boolean, Text
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    __tablename__ = "Users"

    UserId = Column(Integer, primary_key=True, autoincrement=True)
    Username = Column(String(100), unique=True, nullable=False, index=True)
    HashedPassword = Column(String(255), nullable=False)
    Role = Column(String(50), nullable=False, default="viewer")  # viewer, manager, admin
    FullName = Column(String(200), nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)


class ChatSession(Base):
    __tablename__ = "ChatSessions"

    SessionId = Column(String(100), primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("Users.UserId"), nullable=True)
    Title = Column(String(200), default="New Conversation")
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="sessions")


class Customer(Base):
    __tablename__ = "Customers"

    CustomerId = Column(Integer, primary_key=True, autoincrement=True)
    CustomerCode = Column(String(50), unique=True, nullable=False)
    CustomerName = Column(String(200), nullable=False)
    Email = Column(String(200), nullable=True)
    Phone = Column(String(50), nullable=True)
    BillingAddress1 = Column(String(200), nullable=True)
    BillingCity = Column(String(100), nullable=True)
    BillingCountry = Column(String(100), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False)


class Vendor(Base):
    __tablename__ = "Vendors"

    VendorId = Column(Integer, primary_key=True, autoincrement=True)
    VendorCode = Column(String(50), unique=True, nullable=False)
    VendorName = Column(String(200), nullable=False)
    Email = Column(String(200), nullable=True)
    Phone = Column(String(50), nullable=True)
    AddressLine1 = Column(String(200), nullable=True)
    City = Column(String(100), nullable=True)
    Country = Column(String(100), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False)


class Site(Base):
    __tablename__ = "Sites"

    SiteId = Column(Integer, primary_key=True, autoincrement=True)
    SiteCode = Column(String(50), unique=True, nullable=False)
    SiteName = Column(String(200), nullable=False)
    AddressLine1 = Column(String(200), nullable=True)
    City = Column(String(100), nullable=True)
    Country = Column(String(100), nullable=True)
    TimeZone = Column(String(100), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False)


class Location(Base):
    __tablename__ = "Locations"

    LocationId = Column(Integer, primary_key=True, autoincrement=True)
    SiteId = Column(Integer, ForeignKey("Sites.SiteId"), nullable=False)
    LocationCode = Column(String(50), nullable=False)
    LocationName = Column(String(200), nullable=False)
    ParentLocationId = Column(Integer, ForeignKey("Locations.LocationId"), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False)

    site = relationship("Site", backref="locations")


class Item(Base):
    __tablename__ = "Items"

    ItemId = Column(Integer, primary_key=True, autoincrement=True)
    ItemCode = Column(String(100), unique=True, nullable=False)
    ItemName = Column(String(200), nullable=False)
    Category = Column(String(100), nullable=True)
    UnitOfMeasure = Column(String(50), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False)


class Asset(Base):
    __tablename__ = "Assets"

    AssetId = Column(Integer, primary_key=True, autoincrement=True)
    AssetTag = Column(String(100), unique=True, nullable=False)
    AssetName = Column(String(200), nullable=False)
    SiteId = Column(Integer, ForeignKey("Sites.SiteId"), nullable=False)
    LocationId = Column(Integer, ForeignKey("Locations.LocationId"), nullable=True)
    SerialNumber = Column(String(200), nullable=True)
    Category = Column(String(100), nullable=True)
    Status = Column(String(30), default="Active", nullable=False)
    Cost = Column(Numeric(18, 2), nullable=True)
    PurchaseDate = Column(String(50), nullable=True)
    VendorId = Column(Integer, ForeignKey("Vendors.VendorId"), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)

    site = relationship("Site", backref="assets")
    location = relationship("Location", backref="assets")
    vendor = relationship("Vendor", backref="assets")


class Bill(Base):
    __tablename__ = "Bills"

    BillId = Column(Integer, primary_key=True, autoincrement=True)
    VendorId = Column(Integer, ForeignKey("Vendors.VendorId"), nullable=False)
    BillNumber = Column(String(100), nullable=False)
    BillDate = Column(String(50), nullable=False)
    DueDate = Column(String(50), nullable=True)
    TotalAmount = Column(Numeric(18, 2), nullable=False)
    Currency = Column(String(10), default="USD", nullable=False)
    Status = Column(String(30), default="Open", nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)

    vendor = relationship("Vendor", backref="bills")


class PurchaseOrder(Base):
    __tablename__ = "PurchaseOrders"

    POId = Column(Integer, primary_key=True, autoincrement=True)
    PONumber = Column(String(100), unique=True, nullable=False)
    VendorId = Column(Integer, ForeignKey("Vendors.VendorId"), nullable=False)
    PODate = Column(String(50), nullable=False)
    Status = Column(String(30), default="Open", nullable=False)
    SiteId = Column(Integer, ForeignKey("Sites.SiteId"), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)

    vendor = relationship("Vendor", backref="purchase_orders")
    site = relationship("Site", backref="purchase_orders")


class PurchaseOrderLine(Base):
    __tablename__ = "PurchaseOrderLines"

    POLineId = Column(Integer, primary_key=True, autoincrement=True)
    POId = Column(Integer, ForeignKey("PurchaseOrders.POId"), nullable=False)
    LineNumber = Column(Integer, nullable=False)
    ItemId = Column(Integer, ForeignKey("Items.ItemId"), nullable=True)
    ItemCode = Column(String(100), nullable=False)
    Description = Column(String(200), nullable=True)
    Quantity = Column(Numeric(18, 4), nullable=False)
    UnitPrice = Column(Numeric(18, 4), nullable=False)

    po = relationship("PurchaseOrder", backref="lines")
    item = relationship("Item", backref="po_lines")


class SalesOrder(Base):
    __tablename__ = "SalesOrders"

    SOId = Column(Integer, primary_key=True, autoincrement=True)
    SONumber = Column(String(100), unique=True, nullable=False)
    CustomerId = Column(Integer, ForeignKey("Customers.CustomerId"), nullable=False)
    SODate = Column(String(50), nullable=False)
    Status = Column(String(30), default="Open", nullable=False)
    SiteId = Column(Integer, ForeignKey("Sites.SiteId"), nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, nullable=True)

    customer = relationship("Customer", backref="sales_orders")
    site = relationship("Site", backref="sales_orders")


class SalesOrderLine(Base):
    __tablename__ = "SalesOrderLines"

    SOLineId = Column(Integer, primary_key=True, autoincrement=True)
    SOId = Column(Integer, ForeignKey("SalesOrders.SOId"), nullable=False)
    LineNumber = Column(Integer, nullable=False)
    ItemId = Column(Integer, ForeignKey("Items.ItemId"), nullable=True)
    ItemCode = Column(String(100), nullable=False)
    Description = Column(String(200), nullable=True)
    Quantity = Column(Numeric(18, 4), nullable=False)
    UnitPrice = Column(Numeric(18, 4), nullable=False)

    so = relationship("SalesOrder", backref="lines")
    item = relationship("Item", backref="so_lines")


class AssetTransaction(Base):
    __tablename__ = "AssetTransactions"

    AssetTxnId = Column(Integer, primary_key=True, autoincrement=True)
    AssetId = Column(Integer, ForeignKey("Assets.AssetId"), nullable=False)
    FromLocationId = Column(Integer, ForeignKey("Locations.LocationId"), nullable=True)
    ToLocationId = Column(Integer, ForeignKey("Locations.LocationId"), nullable=True)
    TxnType = Column(String(30), nullable=False)
    Quantity = Column(Integer, default=1, nullable=False)
    TxnDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    Note = Column(Text, nullable=True)

    asset = relationship("Asset", backref="transactions")
