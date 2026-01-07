"""
Tests all layers: Database Interface, Operations, and Routers
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import date, timedelta
from typing import Any

# Import modules under test
from hotel.db.db_interface import DBInterface
from hotel.db.models import DBBooking, DBRoom, DBCustomer, to_dict, Base
from hotel.exceptions import (
    ResourceNotFoundException,
    InvalidDateRangeException,
)
from hotel.operations.bookings import (
    read_all_bookings,
    read_booking,
    create_booking,
    delete_booking,
)
from hotel.operations.customers import (
    read_all_customers,
    read_customer,
    create_customer,
    update_customer,
)
from hotel.operations.rooms import read_all_rooms, read_room
from hotel.operations.models import (
    BookingCreateData,
    BookingResult,
    CustomerCreateData,
    CustomerResult,
    CustomerUpdateData,
    RoomResult,
)
from fastapi.testclient import TestClient
from main import app


class TestDatabaseModels(unittest.TestCase):
    """Test database model utility functions"""

    def test_to_dict_with_valid_object(self):
        """Test to_dict converts SQLAlchemy model data correctly"""
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        mock_column1 = Mock()
        mock_column1.name = "id"
        mock_column2 = Mock()
        mock_column2.name = "first_name"
        mock_customer.__table__.columns = [mock_column1, mock_column2]
        mock_customer.id = 1
        mock_customer.first_name = "John"

        result = to_dict(mock_customer)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["first_name"], "John")

    def test_to_dict_with_none_returns_empty_dict(self):
        """Test to_dict returns empty dict when passed None"""
        result = to_dict(None)
        self.assertEqual(result, {})


class TestDBInterface(unittest.TestCase):
    """Test database interface CRUD operations with pagination, filtering, sorting"""

    def setUp(self):
        """Test fixtures"""
        self.mock_session = MagicMock()
        self.mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        self.mock_query.filter.return_value = self.mock_query
        self.mock_query.order_by.return_value = self.mock_query
        self.mock_query.offset.return_value = self.mock_query
        self.mock_query.limit.return_value = self.mock_query
        self.mock_session.query.return_value = self.mock_query
        self.db_interface = DBInterface(DBCustomer)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_default_parameters(self, mock_db_session):
        """Test read_all returns all records with default pagination"""
        mock_db_session.return_value = self.mock_session
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        mock_customer.__table__.columns = []
        self.mock_query.all.return_value = [mock_customer]

        result = self.db_interface.read_all()

        self.mock_query.offset.assert_called_once_with(0)
        self.mock_query.limit.assert_called_once_with(100)
        self.assertEqual(len(result), 1)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_custom_pagination(self, mock_db_session):
        """Test read_all applies skip and limit correctly"""
        mock_db_session.return_value = self.mock_session
        self.mock_query.all.return_value = []

        self.db_interface.read_all(skip=50, limit=200)

        self.mock_query.offset.assert_called_once_with(50)
        self.mock_query.limit.assert_called_once_with(200)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_filters_applied(self, mock_db_session):
        """Test read_all filters records based on provided filters"""
        mock_db_session.return_value = self.mock_session
        self.mock_query.all.return_value = []
        DBCustomer.id = Mock()

        self.db_interface.read_all(filters={"id": 1})

        self.mock_query.filter.assert_called()

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_none_filter_values_ignored(self, mock_db_session):
        """Test read_all ignores None values in filters"""
        mock_db_session.return_value = self.mock_session
        self.mock_query.all.return_value = []

        self.db_interface.read_all(filters={"id": None, "first_name": "test"})

        # Should only filter on non-None values (only first_name should be filtered)
        filter_calls = self.mock_query.filter.call_count
        # Only one filter should be applied (first_name), id=None should be skipped
        self.assertEqual(filter_calls, 1)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_ascending_sort(self, mock_db_session):
        """Test read_all sorts in ascending order"""
        mock_db_session.return_value = self.mock_session
        self.mock_query.all.return_value = []
        mock_column = Mock()
        DBCustomer.id = mock_column

        self.db_interface.read_all(sort_by="id", order="asc")

        mock_column.asc.assert_called_once()

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_descending_sort(self, mock_db_session):
        """Test read_all sorts in descending order"""
        mock_db_session.return_value = self.mock_session
        self.mock_query.all.return_value = []
        mock_column = Mock()
        DBCustomer.id = mock_column

        self.db_interface.read_all(sort_by="id", order="desc")

        mock_column.desc.assert_called_once()

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_invalid_sort_column_ignored(self, mock_db_session):
        """Test read_all ignores invalid sort column names"""
        mock_db_session.return_value = self.mock_session
        self.mock_query.all.return_value = []

        # Should not raise exception
        result = self.db_interface.read_all(sort_by="nonexistent_column")
        self.assertIsInstance(result, list)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_by_id_returns_single_record(self, mock_db_session):
        """Test read_by_id retrieves a single record by ID"""
        mock_db_session.return_value = self.mock_session
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        mock_customer.__table__.columns = []
        self.mock_query.get.return_value = mock_customer

        result = self.db_interface.read_by_id(1)

        self.mock_query.get.assert_called_once_with(1)
        self.assertIsInstance(result, dict)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_by_id_with_nonexistent_id_raises_exception(self, mock_db_session):
        """Test read_by_id raises ResourceNotFoundException for non-existent ID"""
        mock_db_session.return_value = self.mock_session
        self.mock_query.get.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            self.db_interface.read_by_id(999)

    @patch("hotel.db.db_interface.DBSession")
    def test_create_adds_and_commits_record(self, mock_db_session):
        """Test create adds new record to database and commits"""
        mock_db_session.return_value = self.mock_session
        mock_instance = Mock(spec=DBCustomer)
        mock_instance.__table__ = Mock()
        mock_instance.__table__.columns = []

        with patch.object(self.db_interface, "db_class", return_value=mock_instance):
            result = self.db_interface.create({"first_name": "John"})

        self.mock_session.add.assert_called()
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()

    @patch("hotel.db.db_interface.DBSession")
    def test_update_modifies_existing_record(self, mock_db_session):
        """Test update modifies attributes of existing record"""
        mock_db_session.return_value = self.mock_session
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        mock_customer.__table__.columns = []
        self.mock_query.get.return_value = mock_customer

        self.db_interface.update(1, {"first_name": "Jane"})

        self.assertEqual(mock_customer.first_name, "Jane")
        self.mock_session.commit.assert_called_once()

    @patch("hotel.db.db_interface.DBSession")
    def test_delete_removes_record_from_database(self, mock_db_session):
        """Test delete removes record and returns its data"""
        mock_db_session.return_value = self.mock_session
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        mock_customer.__table__.columns = []
        self.mock_query.get.return_value = mock_customer

        result = self.db_interface.delete(1)

        self.mock_session.delete.assert_called_once_with(mock_customer)
        self.mock_session.commit.assert_called_once()
        self.assertIsInstance(result, dict)


class TestBookingOperations(unittest.TestCase):
    """Test booking business logic operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_booking_interface = Mock()
        self.mock_room_interface = Mock()

    def test_read_all_bookings_returns_list_of_results(self):
        """Test read_all_bookings returns list of BookingResult objects"""
        self.mock_booking_interface.read_all.return_value = [
            {
                "id": 1,
                "room_id": 1,
                "customer_id": 1,
                "price": 200,
                "from_date": date(2025, 1, 1),
                "to_date": date(2025, 1, 3),
            }
        ]

        result = read_all_bookings(self.mock_booking_interface)

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], BookingResult)
        self.assertEqual(result[0].id, 1)

    def test_read_all_bookings_passes_pagination_parameters(self):
        """Test read_all_bookings passes skip and limit to interface"""
        self.mock_booking_interface.read_all.return_value = []

        read_all_bookings(self.mock_booking_interface, skip=10, limit=50)

        self.mock_booking_interface.read_all.assert_called_once()
        call_kwargs = self.mock_booking_interface.read_all.call_args[1]
        self.assertEqual(call_kwargs["skip"], 10)
        self.assertEqual(call_kwargs["limit"], 50)

    def test_read_all_bookings_passes_filter_parameters(self):
        """Test read_all_bookings passes filter parameters correctly"""
        self.mock_booking_interface.read_all.return_value = []

        read_all_bookings(
            self.mock_booking_interface, customer_id=5, room_id=3
        )

        call_kwargs = self.mock_booking_interface.read_all.call_args[1]
        self.assertEqual(call_kwargs["filters"]["customer_id"], 5)
        self.assertEqual(call_kwargs["filters"]["room_id"], 3)

    def test_read_all_bookings_passes_sorting_parameters(self):
        """Test read_all_bookings passes sort_by and order parameters"""
        self.mock_booking_interface.read_all.return_value = []

        read_all_bookings(
            self.mock_booking_interface, sort_by="check_in", order="desc"
        )

        call_kwargs = self.mock_booking_interface.read_all.call_args[1]
        self.assertEqual(call_kwargs["sort_by"], "check_in")
        self.assertEqual(call_kwargs["order"], "desc")

    def test_read_booking_returns_single_result(self):
        """Test read_booking returns single BookingResult"""
        self.mock_booking_interface.read_by_id.return_value = {
            "id": 1,
            "room_id": 1,
            "customer_id": 1,
            "price": 200,
            "from_date": date(2025, 1, 1),
            "to_date": date(2025, 1, 3),
        }

        result = read_booking(1, self.mock_booking_interface)

        self.assertIsInstance(result, BookingResult)
        self.assertEqual(result.id, 1)

    def test_create_booking_calculates_price_correctly(self):
        """Test create_booking calculates total price based on days and room price"""
        booking_data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 1, 1),
            to_date=date(2025, 1, 5),
        )
        self.mock_room_interface.read_by_id.return_value = {
            "id": 1,
            "number": "101",
            "size": 2,
            "price": 100,
        }
        self.mock_booking_interface.create.return_value = {
            "id": 1,
            "room_id": 1,
            "customer_id": 1,
            "price": 400,
            "from_date": date(2025, 1, 1),
            "to_date": date(2025, 1, 5),
        }

        result = create_booking(
            booking_data, self.mock_room_interface, self.mock_booking_interface
        )

        # 4 days * 100 per day = 400
        call_args = self.mock_booking_interface.create.call_args[0][0]
        self.assertEqual(call_args["price"], 400)

    def test_create_booking_with_same_day_checkout_raises_error(self):
        """Test create_booking raises InvalidDateRangeException for same-day or negative date ranges"""
        booking_data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 1, 5),
            to_date=date(2025, 1, 5),
        )
        self.mock_room_interface.read_by_id.return_value = {"price": 100}

        with self.assertRaises(InvalidDateRangeException) as context:
            create_booking(
                booking_data, self.mock_room_interface, self.mock_booking_interface
            )

        self.assertIn("after", context.exception.message.lower())

    def test_create_booking_with_past_checkout_before_checkin_raises_error(self):
        """Test create_booking raises InvalidDateRangeException when checkout is before checkin"""
        booking_data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 1, 10),
            to_date=date(2025, 1, 5),
        )
        self.mock_room_interface.read_by_id.return_value = {"price": 100}

        with self.assertRaises(InvalidDateRangeException):
            create_booking(
                booking_data, self.mock_room_interface, self.mock_booking_interface
            )

    def test_delete_booking_returns_deleted_record(self):
        """Test delete_booking returns the deleted booking data"""
        self.mock_booking_interface.delete.return_value = {
            "id": 1,
            "room_id": 1,
            "customer_id": 1,
            "price": 200,
            "from_date": date(2025, 1, 1),
            "to_date": date(2025, 1, 3),
        }

        result = delete_booking(1, self.mock_booking_interface)

        self.assertIsInstance(result, BookingResult)
        self.assertEqual(result.id, 1)
        self.mock_booking_interface.delete.assert_called_once_with(1)


class TestCustomerOperations(unittest.TestCase):
    """Test customer business logic operations"""

    @patch("hotel.operations.customers.DBSession")
    def test_read_all_customers_with_default_parameters(self, mock_db_session):
        """Test read_all_customers returns all customers with defaults"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        result = read_all_customers()

        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)
        self.assertIsInstance(result, list)

    @patch("hotel.operations.customers.DBSession")
    def test_read_all_customers_with_name_filter(self, mock_db_session):
        """Test read_all_customers filters by name using ILIKE"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        read_all_customers(name="John")

        mock_query.filter.assert_called()

    @patch("hotel.operations.customers.DBSession")
    def test_read_all_customers_with_email_filter(self, mock_db_session):
        """Test read_all_customers filters by email using ILIKE"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        read_all_customers(email="@example.com")

        mock_query.filter.assert_called()

    @patch("hotel.operations.customers.DBSession")
    def test_read_all_customers_with_sorting_ascending(self, mock_db_session):
        """Test read_all_customers sorts by specified field in ascending order"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []
        mock_column = Mock()
        DBCustomer.email_address = mock_column

        read_all_customers(sort_by="email_address", order="asc")

        mock_column.asc.assert_called_once()

    @patch("hotel.operations.customers.DBSession")
    def test_read_all_customers_with_pagination(self, mock_db_session):
        """Test read_all_customers applies skip and limit correctly"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        read_all_customers(skip=20, limit=50)

        mock_query.offset.assert_called_once_with(20)
        mock_query.limit.assert_called_once_with(50)

    @patch("hotel.operations.customers.DBSession")
    def test_read_customer_returns_single_customer(self, mock_db_session):
        """Test read_customer returns CustomerResult for valid ID"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        col1 = Mock()
        col1.name = "id"
        col2 = Mock()
        col2.name = "first_name"
        col3 = Mock()
        col3.name = "last_name"
        col4 = Mock()
        col4.name = "email_address"
        mock_customer.__table__.columns = [col1, col2, col3, col4]
        mock_customer.id = 1
        mock_customer.first_name = "John"
        mock_customer.last_name = "Doe"
        mock_customer.email_address = "john@example.com"
        mock_session.query.return_value.get.return_value = mock_customer

        result = read_customer(1)

        self.assertIsInstance(result, CustomerResult)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.first_name, "John")

    @patch("hotel.operations.customers.DBSession")
    def test_create_customer_adds_new_customer(self, mock_db_session):
        """Test create_customer creates new customer record"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        customer_data = CustomerCreateData(
            first_name="Jane",
            last_name="Smith",
            email_address="jane@example.com"
        )
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        col1 = Mock()
        col1.name = "id"
        col2 = Mock()
        col2.name = "first_name"
        col3 = Mock()
        col3.name = "last_name"
        col4 = Mock()
        col4.name = "email_address"
        mock_customer.__table__.columns = [col1, col2, col3, col4]
        mock_customer.id = 1
        mock_customer.first_name = "Jane"
        mock_customer.last_name = "Smith"
        mock_customer.email_address = "jane@example.com"

        with patch("hotel.operations.customers.DBCustomer", return_value=mock_customer):
            result = create_customer(customer_data)

        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()

    @patch("hotel.operations.customers.DBSession")
    def test_update_customer_modifies_existing_customer(self, mock_db_session):
        """Test update_customer updates only provided fields"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        col1 = Mock()
        col1.name = "id"
        col2 = Mock()
        col2.name = "first_name"
        col3 = Mock()
        col3.name = "last_name"
        col4 = Mock()
        col4.name = "email_address"
        mock_customer.__table__.columns = [col1, col2, col3, col4]
        mock_customer.id = 1
        mock_customer.first_name = "John"
        mock_customer.last_name = "Doe"
        mock_customer.email_address = "john@example.com"
        mock_session.query.return_value.get.return_value = mock_customer

        update_data = CustomerUpdateData(first_name="Johnny", last_name=None, email_address=None)
        result = update_customer(1, update_data)

        self.assertEqual(mock_customer.first_name, "Johnny")
        mock_session.commit.assert_called_once()

    @patch("hotel.operations.customers.DBSession")
    def test_update_customer_ignores_none_values(self, mock_db_session):
        """Test update_customer does not update fields set to None"""
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_customer = Mock(spec=DBCustomer)
        mock_customer.__table__ = Mock()
        col1 = Mock()
        col1.name = "id"
        col2 = Mock()
        col2.name = "first_name"
        col3 = Mock()
        col3.name = "last_name"
        col4 = Mock()
        col4.name = "email_address"
        mock_customer.__table__.columns = [col1, col2, col3, col4]
        mock_customer.id = 1
        mock_customer.first_name = "John"
        mock_customer.last_name = "Doe"
        mock_customer.email_address = "john@example.com"
        mock_session.query.return_value.get.return_value = mock_customer

        original_email = mock_customer.email_address
        update_data = CustomerUpdateData(first_name="Johnny", last_name=None, email_address=None)
        result = update_customer(1, update_data)

        # Email should remain unchanged
        self.assertEqual(mock_customer.email_address, original_email)


class TestRoomOperations(unittest.TestCase):
    """Test room business logic operations"""

    @patch("hotel.operations.rooms.DBSession")
    def test_read_all_rooms_with_default_parameters(self, mock_db_session):
        """Test read_all_rooms returns all rooms with default pagination"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        result = read_all_rooms()

        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)
        self.assertIsInstance(result, list)

    @patch("hotel.operations.rooms.DBSession")
    @patch("hotel.operations.rooms.DBRoom")
    def test_read_all_rooms_with_availability_filter(self, mock_db_room, mock_db_session):
        """Test read_all_rooms filters by availability status"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []
        # Mock the available attribute
        mock_db_room.available = Mock()

        read_all_rooms(available=True)

        mock_query.filter.assert_called()

    @patch("hotel.operations.rooms.DBSession")
    def test_read_all_rooms_with_price_range_filters(self, mock_db_session):
        """Test read_all_rooms filters by min and max price"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        read_all_rooms(min_price=50.0, max_price=200.0)

        # Should call filter twice (once for min, once for max)
        self.assertEqual(mock_query.filter.call_count, 2)

    @patch("hotel.operations.rooms.DBSession")
    def test_read_all_rooms_with_sorting(self, mock_db_session):
        """Test read_all_rooms sorts by price in descending order"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []
        mock_column = Mock()
        DBRoom.price = mock_column

        read_all_rooms(sort_by="price", order="desc")

        mock_column.desc.assert_called_once()

    @patch("hotel.operations.rooms.DBSession")
    def test_read_all_rooms_with_pagination(self, mock_db_session):
        """Test read_all_rooms applies custom pagination"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        read_all_rooms(skip=10, limit=25)

        mock_query.offset.assert_called_once_with(10)
        mock_query.limit.assert_called_once_with(25)

    @patch("hotel.operations.rooms.DBSession")
    def test_read_room_returns_single_room(self, mock_db_session):
        """Test read_room returns RoomResult for valid room ID"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_room = Mock(spec=DBRoom)
        mock_room.__table__ = Mock()
        col1 = Mock()
        col1.name = "id"
        col2 = Mock()
        col2.name = "number"
        col3 = Mock()
        col3.name = "size"
        col4 = Mock()
        col4.name = "price"
        mock_room.__table__.columns = [col1, col2, col3, col4]
        mock_room.id = 1
        mock_room.number = "101"
        mock_room.size = 2
        mock_room.price = 150
        mock_session.query.return_value.get.return_value = mock_room

        result = read_room(1)

        self.assertIsInstance(result, RoomResult)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.number, "101")


class TestRouterEndpoints(unittest.TestCase):
    """Test FastAPI router endpoints with validation"""

    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)

    @patch("hotel.routers.bookings.read_all_bookings")
    @patch("hotel.routers.bookings.DBInterface")
    def test_get_bookings_with_default_parameters(self, mock_interface, mock_read_all):
        """Test GET /bookings endpoint with default query parameters"""
        mock_read_all.return_value = []

        response = self.client.get("/bookings")

        self.assertEqual(response.status_code, 200)
        mock_read_all.assert_called_once()

    @patch("hotel.routers.bookings.read_all_bookings")
    @patch("hotel.routers.bookings.DBInterface")
    def test_get_bookings_with_pagination_parameters(self, mock_interface, mock_read_all):
        """Test GET /bookings accepts skip and limit query params"""
        mock_read_all.return_value = []

        response = self.client.get("/bookings?skip=10&limit=50")

        self.assertEqual(response.status_code, 200)
        call_kwargs = mock_read_all.call_args[1]
        self.assertEqual(call_kwargs["skip"], 10)
        self.assertEqual(call_kwargs["limit"], 50)

    @patch("hotel.routers.bookings.read_all_bookings")
    @patch("hotel.routers.bookings.DBInterface")
    def test_get_bookings_with_filter_parameters(self, mock_interface, mock_read_all):
        """Test GET /bookings accepts customer_id and room_id filters"""
        mock_read_all.return_value = []

        response = self.client.get("/bookings?customer_id=5&room_id=3")

        self.assertEqual(response.status_code, 200)
        call_kwargs = mock_read_all.call_args[1]
        self.assertEqual(call_kwargs["customer_id"], 5)
        self.assertEqual(call_kwargs["room_id"], 3)

    @patch("hotel.routers.bookings.read_all_bookings")
    @patch("hotel.routers.bookings.DBInterface")
    def test_get_bookings_validates_limit_maximum(self, mock_interface, mock_read_all):
        """Test GET /bookings rejects limit > 1000"""
        response = self.client.get("/bookings?limit=1500")

        self.assertEqual(response.status_code, 422)  # Validation error

    @patch("hotel.routers.bookings.read_all_bookings")
    @patch("hotel.routers.bookings.DBInterface")
    def test_get_bookings_validates_skip_minimum(self, mock_interface, mock_read_all):
        """Test GET /bookings rejects negative skip values"""
        response = self.client.get("/bookings?skip=-5")

        self.assertEqual(response.status_code, 422)  # Validation error

    @patch("hotel.routers.bookings.read_booking")
    @patch("hotel.routers.bookings.DBInterface")
    def test_get_booking_by_id_with_valid_id(self, mock_interface, mock_read):
        """Test GET /booking/{booking_id} returns booking for valid ID"""
        mock_booking = BookingResult(
            id=1,
            room_id=1,
            customer_id=1,
            price=200,
            from_date=date(2025, 1, 1),
            to_date=date(2025, 1, 3),
        )
        mock_read.return_value = mock_booking

        response = self.client.get("/booking/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 1)

    @patch("hotel.routers.bookings.read_booking")
    @patch("hotel.routers.bookings.DBInterface")
    def test_get_booking_validates_positive_id(self, mock_interface, mock_read):
        """Test GET /booking/{booking_id} rejects zero or negative IDs"""
        response = self.client.get("/booking/0")

        self.assertEqual(response.status_code, 422)  # Validation error

    @patch("hotel.routers.bookings.delete_booking")
    @patch("hotel.routers.bookings.DBInterface")
    def test_delete_booking_with_valid_id(self, mock_interface, mock_delete):
        """Test DELETE /booking/{booking_id} deletes booking"""
        mock_booking = BookingResult(
            id=1,
            room_id=1,
            customer_id=1,
            price=200,
            from_date=date(2025, 1, 1),
            to_date=date(2025, 1, 3),
        )
        mock_delete.return_value = mock_booking

        response = self.client.delete("/booking/1")

        self.assertEqual(response.status_code, 200)
        mock_delete.assert_called_once()

    @patch("hotel.routers.customers.read_all_customers")
    def test_get_customers_with_name_filter(self, mock_read_all):
        """Test GET /customers filters by name"""
        mock_read_all.return_value = []

        response = self.client.get("/customers?name=John")

        self.assertEqual(response.status_code, 200)
        call_kwargs = mock_read_all.call_args[1]
        self.assertEqual(call_kwargs["name"], "John")

    @patch("hotel.routers.customers.read_all_customers")
    def test_get_customers_with_email_filter(self, mock_read_all):
        """Test GET /customers filters by email"""
        mock_read_all.return_value = []

        response = self.client.get("/customers?email=@example.com")

        self.assertEqual(response.status_code, 200)
        call_kwargs = mock_read_all.call_args[1]
        self.assertEqual(call_kwargs["email"], "@example.com")

    @patch("hotel.routers.customers.read_all_customers")
    def test_get_customers_with_sorting(self, mock_read_all):
        """Test GET /customers sorts by specified field"""
        mock_read_all.return_value = []

        response = self.client.get("/customers?sort_by=email&order=desc")

        self.assertEqual(response.status_code, 200)
        call_kwargs = mock_read_all.call_args[1]
        self.assertEqual(call_kwargs["sort_by"], "email")
        self.assertEqual(call_kwargs["order"], "desc")

    @patch("hotel.routers.customers.read_customer")
    def test_get_customer_by_id_validates_positive_id(self, mock_read):
        """Test GET /customer/{customer_id} rejects non-positive IDs"""
        response = self.client.get("/customer/-1")

        self.assertEqual(response.status_code, 422)  # Validation error

    @patch("hotel.routers.customers.create_customer")
    def test_post_customer_creates_new_customer(self, mock_create):
        """Test POST /customer creates new customer with valid data"""
        mock_customer = CustomerResult(
            id=1,
            first_name="Jane",
            last_name="Doe",
            email_address="jane@example.com"
        )
        mock_create.return_value = mock_customer

        response = self.client.post(
            "/customer",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email_address": "jane@example.com"
            }
        )

        self.assertEqual(response.status_code, 200)
        mock_create.assert_called_once()

    @patch("hotel.routers.customers.update_customer")
    def test_patch_customer_validates_positive_id(self, mock_update):
        """Test PATCH /customer/{customer_id} rejects non-positive IDs"""
        response = self.client.patch(
            "/customer/0",
            json={"first_name": "Updated"}
        )

        self.assertEqual(response.status_code, 422)  # Validation error

    @patch("hotel.routers.rooms.read_all_rooms")
    def test_get_rooms_with_availability_filter(self, mock_read_all):
        """Test GET /rooms filters by availability"""
        mock_read_all.return_value = []

        response = self.client.get("/rooms?available=true")

        self.assertEqual(response.status_code, 200)
        call_kwargs = mock_read_all.call_args[1]
        self.assertEqual(call_kwargs["available"], True)

    @patch("hotel.routers.rooms.read_all_rooms")
    def test_get_rooms_with_price_range(self, mock_read_all):
        """Test GET /rooms filters by price range"""
        mock_read_all.return_value = []

        response = self.client.get("/rooms?min_price=50&max_price=200")

        self.assertEqual(response.status_code, 200)
        call_kwargs = mock_read_all.call_args[1]
        self.assertEqual(call_kwargs["min_price"], 50)
        self.assertEqual(call_kwargs["max_price"], 200)

    @patch("hotel.routers.rooms.read_all_rooms")
    def test_get_rooms_validates_negative_prices(self, mock_read_all):
        """Test GET /rooms rejects negative price values"""
        response = self.client.get("/rooms?min_price=-10")

        self.assertEqual(response.status_code, 422)  # Validation error

    @patch("hotel.routers.rooms.read_room")
    def test_get_room_by_id_validates_positive_id(self, mock_read):
        """Test GET /room/{room_id} rejects non-positive IDs"""
        response = self.client.get("/room/0")

        self.assertEqual(response.status_code, 422)  # Validation error

    def test_root_endpoint_returns_message(self):
        """Test GET / returns welcome message"""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), str)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_booking_create_data_with_minimum_valid_date_range(self):
        """Test BookingCreateData accepts (min) 1-day booking"""
        data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 1, 1),
            to_date=date(2025, 1, 2),
        )
        self.assertEqual((data.to_date - data.from_date).days, 1)

    def test_customer_create_data_with_empty_strings(self):
        """Test CustomerCreateData validation with empty strings"""
        # Pydantic should accept empty strings by default
        data = CustomerCreateData(
            first_name="",
            last_name="",
            email_address=""
        )
        self.assertEqual(data.first_name, "")

    def test_customer_update_data_with_all_none_values(self):
        """Test CustomerUpdateData with all optional fields as None"""
        data = CustomerUpdateData(
            first_name=None,
            last_name=None,
            email_address=None
        )
        # Should exclude all None values
        dict_data = data.model_dump(exclude_none=True)
        self.assertEqual(len(dict_data), 0)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_zero_limit(self, mock_db_session):
        """Test read_all with limit=0 returns empty list"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        db_interface = DBInterface(DBCustomer)
        result = db_interface.read_all(limit=0)

        mock_query.limit.assert_called_once_with(0)
        self.assertEqual(len(result), 0)

    @patch("hotel.db.db_interface.DBSession")
    def test_read_all_with_large_skip_value(self, mock_db_session):
        """Test read_all handles very large skip values"""
        mock_session = MagicMock()
        mock_db_session.return_value = mock_session
        mock_query = MagicMock()
        # Make query methods return mock_query for chaining
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        db_interface = DBInterface(DBCustomer)
        result = db_interface.read_all(skip=1000000)

        mock_query.offset.assert_called_once_with(1000000)
        self.assertEqual(len(result), 0)

    def test_booking_result_with_zero_price(self):
        """Test BookingResult accepts zero price"""
        booking = BookingResult(
            id=1,
            room_id=1,
            customer_id=1,
            price=0,
            from_date=date(2025, 1, 1),
            to_date=date(2025, 1, 2),
        )
        self.assertEqual(booking.price, 0)

    def test_room_result_with_large_price(self):
        """Test RoomResult handles very large price values"""
        room = RoomResult(
            id=1,
            number="SUITE-1",
            size=10,
            price=999999
        )
        self.assertEqual(room.price, 999999)


if __name__ == "__main__":
    unittest.main()
