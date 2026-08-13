import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.connection import engine, Base, SessionLocal
from app.database.models import (
    User, Customer, Vendor, Site, Location, Item, Asset,
    Bill, PurchaseOrder, PurchaseOrderLine, SalesOrder, SalesOrderLine, AssetTransaction
)
from app.security.auth import get_password_hash


def init_db():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


def seed_db():
    session = SessionLocal()
    try:
        # Check if already seeded
        if session.query(Vendor).first() is not None:
            print("Database already contains data. Skipping initial seeding.")
            return

        print("Seeding initial users for RBAC...")
        users = [
            User(Username="admin", HashedPassword=get_password_hash("admin123"), Role="admin", FullName="System Admin"),
            User(Username="manager", HashedPassword=get_password_hash("manager123"), Role="manager", FullName="Operations Manager"),
            User(Username="viewer", HashedPassword=get_password_hash("viewer123"), Role="viewer", FullName="Inventory Viewer"),
        ]
        session.add_all(users)

        print("Seeding vendors...")
        vendors = [
            Vendor(VendorCode="V001", VendorName="Acme Corp", Email="contact@acme.com", Phone="555-0100", AddressLine1="123 Main St", City="New York", Country="USA"),
            Vendor(VendorCode="V002", VendorName="TechSupply Inc", Email="sales@techsupply.com", Phone="555-0101", AddressLine1="456 Tech Blvd", City="San Jose", Country="USA"),
            Vendor(VendorCode="V003", VendorName="Global Office Needs", Email="hello@globaloffice.com", Phone="555-0102", AddressLine1="789 Business Rd", City="London", Country="UK")
        ]
        session.add_all(vendors)
        session.flush()

        print("Seeding customers...")
        customers = [
            Customer(CustomerCode="C001", CustomerName="Beta Industries", Email="billing@beta.com", Phone="555-0200", BillingAddress1="321 Customer Ave", BillingCity="Chicago", BillingCountry="USA"),
            Customer(CustomerCode="C002", CustomerName="Omega Services", Email="accounts@omega.com", Phone="555-0201", BillingAddress1="654 Client Pkwy", BillingCity="Austin", BillingCountry="USA")
        ]
        session.add_all(customers)

        print("Seeding sites...")
        sites = [
            Site(SiteCode="S01", SiteName="Headquarters", AddressLine1="100 HQ Drive", City="New York", Country="USA", TimeZone="EST"),
            Site(SiteCode="S02", SiteName="West Coast Warehouse", AddressLine1="200 Logistics Way", City="Los Angeles", Country="USA", TimeZone="PST"),
            Site(SiteCode="S03", SiteName="European Hub", AddressLine1="300 Euro Blvd", City="Berlin", Country="Germany", TimeZone="CET")
        ]
        session.add_all(sites)
        session.flush()

        print("Seeding locations...")
        locations = [
            Location(SiteId=sites[0].SiteId, LocationCode="HQ-FL1", LocationName="Floor 1 Storage"),
            Location(SiteId=sites[0].SiteId, LocationCode="HQ-IT", LocationName="IT Department"),
            Location(SiteId=sites[1].SiteId, LocationCode="WC-A1", LocationName="Aisle 1"),
            Location(SiteId=sites[1].SiteId, LocationCode="WC-A2", LocationName="Aisle 2"),
            Location(SiteId=sites[2].SiteId, LocationCode="EU-MAIN", LocationName="Main Storage")
        ]
        session.add_all(locations)
        session.flush()

        print("Seeding items...")
        items = [
            Item(ItemCode="ITM-001", ItemName="ThinkPad T14", Category="Electronics", UnitOfMeasure="EA"),
            Item(ItemCode="ITM-002", ItemName="Ergonomic Chair", Category="Furniture", UnitOfMeasure="EA"),
            Item(ItemCode="ITM-003", ItemName="Wireless Mouse", Category="Accessories", UnitOfMeasure="EA"),
            Item(ItemCode="ITM-004", ItemName="HDMI Cable 6ft", Category="Cables", UnitOfMeasure="EA"),
            Item(ItemCode="ITM-005", ItemName="Standing Desk", Category="Furniture", UnitOfMeasure="EA")
        ]
        session.add_all(items)
        session.flush()

        print("Seeding assets...")
        assets = [
            Asset(AssetTag="TAG-1001", AssetName="Lenovo ThinkPad T14 - Gen1", SiteId=sites[0].SiteId, LocationId=locations[1].LocationId, SerialNumber="SN123456", Category="Electronics", Status="Active", Cost=1200.00, PurchaseDate="2025-01-15", VendorId=vendors[0].VendorId),
            Asset(AssetTag="TAG-1002", AssetName="Lenovo ThinkPad T14 - Gen2", SiteId=sites[0].SiteId, LocationId=locations[1].LocationId, SerialNumber="SN123457", Category="Electronics", Status="In Repair", Cost=1250.00, PurchaseDate="2025-02-01", VendorId=vendors[0].VendorId),
            Asset(AssetTag="TAG-1003", AssetName="Herman Miller Chair", SiteId=sites[0].SiteId, LocationId=locations[0].LocationId, SerialNumber="SN998877", Category="Furniture", Status="Active", Cost=800.00, PurchaseDate="2024-11-20", VendorId=vendors[2].VendorId),
            Asset(AssetTag="TAG-1004", AssetName="Dell Monitor 27\"", SiteId=sites[1].SiteId, LocationId=locations[2].LocationId, SerialNumber="SN554433", Category="Electronics", Status="Active", Cost=300.00, PurchaseDate="2025-03-01", VendorId=vendors[1].VendorId),
            Asset(AssetTag="TAG-1005", AssetName="Cisco Switch", SiteId=sites[2].SiteId, LocationId=locations[4].LocationId, SerialNumber="SN112233", Category="Networking", Status="Active", Cost=1500.00, PurchaseDate="2024-06-10", VendorId=vendors[1].VendorId)
        ]
        session.add_all(assets)
        session.flush()

        print("Seeding bills...")
        bills = [
            Bill(VendorId=vendors[0].VendorId, BillNumber="B-2025-001", BillDate="2025-01-10", DueDate="2025-02-10", TotalAmount=5000.00, Currency="USD", Status="Paid"),
            Bill(VendorId=vendors[1].VendorId, BillNumber="B-2025-002", BillDate="2025-02-15", DueDate="2025-03-15", TotalAmount=1250.00, Currency="USD", Status="Open"),
            Bill(VendorId=vendors[2].VendorId, BillNumber="B-2025-003", BillDate="2025-03-01", DueDate="2025-03-31", TotalAmount=300.00, Currency="GBP", Status="Open")
        ]
        session.add_all(bills)

        print("Seeding purchase orders...")
        pos = [
            PurchaseOrder(PONumber="PO-10001", VendorId=vendors[0].VendorId, PODate="2025-01-05", Status="Closed", SiteId=sites[0].SiteId),
            PurchaseOrder(PONumber="PO-10002", VendorId=vendors[1].VendorId, PODate="2025-02-01", Status="Open", SiteId=sites[0].SiteId),
            PurchaseOrder(PONumber="PO-10003", VendorId=vendors[2].VendorId, PODate="2025-02-20", Status="Open", SiteId=sites[2].SiteId)
        ]
        session.add_all(pos)
        session.flush()

        print("Seeding purchase order lines...")
        po_lines = [
            PurchaseOrderLine(POId=pos[0].POId, LineNumber=1, ItemId=items[0].ItemId, ItemCode="ITM-001", Description="ThinkPad T14", Quantity=10.0, UnitPrice=1200.00),
            PurchaseOrderLine(POId=pos[0].POId, LineNumber=2, ItemId=items[3].ItemId, ItemCode="ITM-004", Description="HDMI Cable 6ft", Quantity=50.0, UnitPrice=15.00),
            PurchaseOrderLine(POId=pos[0].POId, LineNumber=3, ItemId=items[1].ItemId, ItemCode="ITM-002", Description="Ergonomic Chair", Quantity=5.0, UnitPrice=250.00)
        ]
        session.add_all(po_lines)

        print("Seeding sales orders...")
        sos = [
            SalesOrder(SONumber="SO-50001", CustomerId=customers[0].CustomerId, SODate="2025-02-10", Status="Shipped", SiteId=sites[0].SiteId),
            SalesOrder(SONumber="SO-50002", CustomerId=customers[1].CustomerId, SODate="2025-03-01", Status="Processing", SiteId=sites[1].SiteId)
        ]
        session.add_all(sos)
        session.flush()

        print("Seeding sales order lines...")
        so_lines = [
            SalesOrderLine(SOId=sos[0].SOId, LineNumber=1, ItemId=items[0].ItemId, ItemCode="ITM-001", Description="ThinkPad T14", Quantity=2.0, UnitPrice=1500.00),
            SalesOrderLine(SOId=sos[0].SOId, LineNumber=2, ItemId=items[2].ItemId, ItemCode="ITM-003", Description="Wireless Mouse", Quantity=5.0, UnitPrice=45.00),
            SalesOrderLine(SOId=sos[1].SOId, LineNumber=1, ItemId=items[1].ItemId, ItemCode="ITM-002", Description="Ergonomic Chair", Quantity=1.0, UnitPrice=350.00)
        ]
        session.add_all(so_lines)

        print("Seeding asset transactions...")
        txns = [
            AssetTransaction(AssetId=assets[0].AssetId, FromLocationId=None, ToLocationId=locations[0].LocationId, TxnType="Receipt", Quantity=1, Note="Initial setup for Tag 1001"),
            AssetTransaction(AssetId=assets[1].AssetId, FromLocationId=None, ToLocationId=locations[0].LocationId, TxnType="Receipt", Quantity=1, Note="Initial setup for Tag 1002"),
            AssetTransaction(AssetId=assets[1].AssetId, FromLocationId=locations[0].LocationId, ToLocationId=locations[1].LocationId, TxnType="Transfer", Quantity=1, Note="Moved to IT for repair"),
            AssetTransaction(AssetId=assets[2].AssetId, FromLocationId=None, ToLocationId=locations[4].LocationId, TxnType="Receipt", Quantity=1, Note="Received in EU Main")
        ]
        session.add_all(txns)

        session.commit()
        print("Database initialized and seeded successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
    seed_db()
