from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db.models import Q

from .models import *
from .forms import *

import datetime

def account_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
            messages.success(request, "Successfully logged in")
            return redirect(reverse("home"))
        else:
            # Return a 'disabled account' error message
            messages.info(request, "This account has been disabled")
            return redirect(reverse("home"))

    else:
        # Return an 'invalid login' error message.
        messages.error(request, "Invalid username or password")
        return redirect(reverse("acct_login"))


def account_logout(request):
    logout(request)
    messages.success(request, "Successfully logged out")

    return redirect(reverse("home"))


def count_transaction_totals(item):
    count = 0
    for transaction in item.transactions:
        count += transaction.entity_quantity

    return count


def find_list_items(start_date, end_date, transaction_type):
    transactions = TransactionLog.objects.filter(entry_date__range=[start_date, end_date])

    list_items = []

    class InventoryItem():
        item_id = ""
        item_number = ""
        transactions = ""

        def __init__(self, item_number=""):
            self.item_number = item_number

    found_items = transactions.filter(entry_type=transaction_type)
    unique_items = found_items.values('entity_number').distinct()

    for unique_item in unique_items:
        db_item = Item.objects.get(id=unique_item['entity_number'])

        item = InventoryItem()
        item.item_id = db_item.id
        item.item_number = "%s - %s" % (db_item.item_number, db_item.description)
        item.transactions = found_items.filter(entity_number=unique_item['entity_number'])

        if item not in list_items:
            list_items.append(item)

    list_items = sorted(list_items, key=lambda x: x.item_number, reverse=False)
    return list_items


@login_required
def index(request):
    dict_return = {'title': "Inventory Tracking"}

    return render(request, 'inventory/index.html', dict_return)


@login_required
def inventory_add(request):
    dict_return = {'title': "Add New Inventory Item"}

    if request.method == 'POST':
        # check response
        form = InventoryForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            vendor = cd['vendor']

            item = Item(
                item_number=cd["itemnumber"],
                description=cd["description"],
                vendor_name=vendor,
                quantity=cd["quantity"],
                cost=cd["cost"],
                hidden=0
            )

            try:
                item.save()
            except:
                messages.error(request, "There was an error saving this new item")
                return redirect("list_inventory")
            else:
                log_transaction('IAD', item.id)
                messages.success(request, "Saved new item [%s]" % cd['itemnumber'])
                return redirect("list_inventory")

        else:
            dict_return['form'] = form
    else:
        form = InventoryForm()
        dict_return['form'] = form
        dict_return['vendorform'] = VendorForm()

    return render(request, "inventory/add.html", dict_return)


@login_required
def inventory_delete(request, itemid):
    try:
        item = Item.objects.get(id=itemid)
    except Item.DoesNotExist:
        messages.error(request, "The item searched does not exist")
        return redirect("list_inventory")

    item_id = item.id
    item_number = item.item_number

    try:
        item.delete()
    except:
        messages.error(request, "There was an error deleting this item")
    else:
        log_transaction('IDL', item_id)
        messages.success(request, "Deleted item [%s]" % item_number)

    return redirect("list_inventory")


@login_required
def inventory_edit(request, itemid):
    dict_return = {}

    try:
        item = Item.objects.get(id=itemid)
    except Item.DoesNotExist:
        messages.error(request, "The item searched does not exist")
        return redirect("list_inventory")

    dict_return['title'] = "Edit %s" % item.item_number

    if request.method == 'POST':
        # check response
        form = InventoryForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if item.item_number != cd['itemnumber']:
                item.item_number = cd['itemnumber']

            if item.description != cd['description']:
                item.description = cd['description']

            if str(item.quantity) != cd['quantity']:
                item.quantity = cd['quantity']

            if str(item.cost) != cd['cost']:
                item.cost = cd['cost']

            if item.vendor_name != cd['vendor']:
                item.vendor_name = cd['vendor']

            if item.hidden != cd['hidden']:
                item.hidden = cd['hidden']

            try:
                item.save()
            except:
                messages.error(request, "There was an error saving these changes")
                return redirect("list_inventory")
            else:
                messages.success(request, "Saved changes")

                return redirect("list_inventory")

        else:
            dict_return['form'] = form
    else:
        form = InventoryForm(initial={
            "itemnumber": item.item_number,
            "description": item.description,
            "vendor": item.vendor_name_id,
            "quantity": item.quantity,
            "cost": item.cost,
            "hidden": item.hidden,
        })

        dict_return['form'] = form

    return render(request, "inventory/edit.html", dict_return)


@login_required
def inventory_list(request, show_deleted=False):
    dict_return = {}
    items = None

    if show_deleted:
        dict_return['title'] = "Inventory Administration - Showing Items Marked Deleted"
    else:
        dict_return['title'] = "Inventory Administration"

    if request.method == 'POST':
        if 'filter' in request.POST and request.POST['filter']:
            search = request.POST['filter']
            dict_return['search'] = search

            if show_deleted:
                # Check the item number
                items = Item.objects.filter(item_number__icontains=search).order_by("item_number")

                if len(items) == 0:
                    # Check the description
                    items = Item.objects.filter(description__icontains=search).order_by("item_number")

                if len(items) == 0:
                    # Check the vendors
                    items = Item.objects.filter(vendor_name__vendor_name__icontains=search).order_by("item_number")

                if len(items) == 0:
                    messages.info(request, "Could not find anything that contains your search phrase [%s]" % search)
                    items = ""
            else:
                # Check the item number
                items = Item.objects.filter(item_number__icontains=search).exclude(hidden=1).order_by("item_number")

                if len(items) == 0:
                    # Check the description
                    items = Item.objects\
                        .filter(Q(description__icontains=search) | Q(vendor_name__vendor_name__icontains=search))\
                        .exclude(hidden=1).order_by("item_number")

                if len(items) == 0:
                    messages.info(request, "Could not find anything that contains your search phrase [%s]" % search)
                    items = ""

            dict_return['items'] = items

    else:

        if show_deleted:
            # Return a list of all items including deleted items
            items = Item.objects.all().order_by("item_number")
        else:
            # Return a list of all items excluding deleted items
            items = Item.objects.all().exclude(hidden=1).order_by("item_number")

    dict_return['items'] = items

    return render(request, "inventory/list.html", dict_return)


def log_transaction(entry_type, entity_number, entity_quantity=None):

    transaction_entry = TransactionLog()
    transaction_entry.entry_type = entry_type
    transaction_entry.entity_number = entity_number
    transaction_entry.entity_quantity = entity_quantity

    transaction_entry.save()


@login_required
def receive_inventory(request):
    dict_return = {'title': "Record Received Items", 'buttonaction': "Receive"}

    if request.method == 'POST':
        # check response
        form_return = QuantityForm(request.POST)

        if form_return.is_valid():
            cd = form_return.cleaned_data
            item = cd['item']

            item.quantity = item.quantity + cd['quantity']

            try:
                item.save()
            except:
                messages.error(request, "There was a problem updating the quantity for item [%s]" % item.description)
            else:
                log_transaction('RCV', item.id, int(cd['quantity']))

                transaction = {
                        "type": "Received",
                        "item_number": "%s - %s" % (item.item_number, item.description),
                        "quantity_actioned": cd['quantity'],
                        "quantity_remaining": item.quantity,
                    }

                dict_return['transaction'] = transaction
                dict_return['title'] = "Transaction Recorded - %s" % datetime.datetime.now()\
                    .strftime("%m/%d/%Y %-I:%M %p")

                return render(request, "reports/transaction_record.html", dict_return)

            return redirect("receive_inventory")

        else:
            dict_return['form'] = form_return

    else:
        form = QuantityForm(initial={
            "quantity": 0
        })

        dict_return['form'] = form

    return render(request, "inventory/ship_receive.html", dict_return)


@login_required
def ship_inventory(request):
    dict_return = {'title': "Record Shipped Items", 'buttonaction': "Ship"}

    if request.method == 'POST':
        # check response
        form = QuantityForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            item = cd['item']

            # Check item quantity to see if they have enough items to ship
            if item.quantity < cd['quantity']:
                messages.error(request,
                               "You do not have enough items in your inventory to ship the quantity [%s] you entered" %
                               cd['quantity'])
                messages.info(request, "You have a quantity of %s   items for %s" % (item.quantity, item.description))
            else:
                item.quantity = item.quantity - cd['quantity']

                try:
                    item.save()
                except:
                    messages.error(request,
                                   "There was a problem updating the quantity for item [%s]" % item.description)
                else:
                    log_transaction('SHP', item.id, int(cd['quantity']))

                    transaction = {
                        "type": "Shipped",
                        "item_number": "%s - %s" % (item.item_number, item.description),
                        "quantity_actioned": cd['quantity'],
                        "quantity_remaining": item.quantity,
                    }

                    dict_return['transaction'] = transaction
                    dict_return['title'] = "Transaction Recorded - %s" % datetime.datetime.now()\
                        .strftime("%m/%d/%Y %-I:%M %p")

                    return render(request, "reports/transaction_record.html", dict_return)

            return redirect("ship_inventory")

        else:
            dict_return['form'] = form
    else:
        form = QuantityForm(initial={
            "quantity": 0,
        })

        dict_return['form'] = form

    return render(request, "inventory/ship_receive.html", dict_return)


@login_required
def report_daily_transactions(request, day):
    dict_return = {}

    start_date = None
    end_date = None

    if day.lower() == "today":
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=1)
        dict_return['title'] = "Transaction Report - %s" % start_date.strftime("%m/%d/%Y")
    elif day.lower() == "yesterday":
        start_date = datetime.date.today() - datetime.timedelta(days=1)
        end_date = start_date + datetime.timedelta(days=1)
        dict_return['title'] = "Transaction Report - %s" % start_date.strftime("%m/%d/%Y")
    elif day.lower() == "last_week":
        start_date = datetime.date.today() - datetime.timedelta(days=7)
        end_date = datetime.date.today() + datetime.timedelta(days=1)
        dict_return['title'] = "Transaction Report - Last 7 days"
    elif day.lower() == "custom":
        post_start_date = request.POST['start_date'].split("/")
        post_end_date = request.POST['end_date'].split("/")
        start_date = datetime.date(int(post_start_date[2]), int(post_start_date[0]), int(post_start_date[1]))
        end_date = datetime.date(int(post_end_date[2]), int(post_end_date[0]), int(post_end_date[1]))
        dict_return['title'] = "Custom Transaction Report - [%s - %s]" % (request.POST['start_date'],
                                                                          request.POST['end_date'])

    shipped_items = find_list_items(start_date, end_date, 'SHP')
    dict_return['shipped_items'] = shipped_items

    received_items = find_list_items(start_date, end_date, 'RCV')
    dict_return['received_items'] = received_items

    unique_list_touched_items = []
    class TouchedItems():
        item_number = ""
        shipped = 0
        received = 0
        remaining = 0

        def __init__(self, item_number=""):
            self.item_number = item_number

    # First make a unique list of touched items - then we can fill in the data
    for shipped_item in shipped_items:
        if shipped_item.item_id not in unique_list_touched_items:
            unique_list_touched_items.append(shipped_item.item_id)

    for received_item in received_items:
        if received_item.item_id not in unique_list_touched_items:
            unique_list_touched_items.append(received_item.item_id)

    # Now for each item - determine how many things were shipped and received
    list_touched_items = []
    for unique_item in unique_list_touched_items:
        touched_item = TouchedItems()

        for shipped_item in shipped_items:
            if shipped_item.item_id == unique_item:
                touched_item.shipped = count_transaction_totals(shipped_item)

        for received_item in received_items:
            if received_item.item_id == unique_item:
                touched_item.received = count_transaction_totals(received_item)

        db_item = Item.objects.get(id=unique_item)
        touched_item.item_number = "%s - %s" % (db_item.item_number, db_item.description)
        touched_item.remaining = db_item.quantity

        if touched_item not in list_touched_items:
            list_touched_items.append(touched_item)

    list_touched_items = sorted(list_touched_items, key=lambda x: x.item_number, reverse=False)
    dict_return['total_items'] = list_touched_items

    return render(request, "reports/transaction_report.html", dict_return)


@login_required
def report_full_inventory(request):
    dict_return = {'title': "Generate Reports"}
    items = None

    if request.method == 'POST':
        if 'filter' in request.POST and request.POST['filter']:
            search = request.POST['filter']

            # Check the item number
            items = Item.objects.filter(item_number__icontains=search).exclude(hidden=1).order_by("item_number")

            if len(items) == 0:
                # Check the description
                items = Item.objects \
                    .filter(Q(description__icontains=search) | Q(vendor_name__vendor_name__icontains=search)) \
                    .exclude(hidden=1).order_by("item_number")

            if len(items) == 0:
                messages.info(request, "Could not find anything that contains your search phrase [%s]" % search)
                items = ""

            dict_return['items'] = items

    else:
        # Return a list of all the items
        items = Item.objects.all().exclude(hidden=1).order_by("item_number")

    dict_return['items'] = items

    # Calculate Grand Total for requested entry
    grand_total = 0
    for item in items:
        item_total = item.quantity * item.cost
        grand_total = grand_total + item_total

    dict_return['grand_total'] = float(grand_total)

    return render(request, "reports/report_inventory_full.html", dict_return)


@login_required
def vendor_add(request):
    if request.method == 'POST':
        # check response
        form = VendorForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # First check to see if there is a vendor with that name
            try:
                Vendor.objects.get(vendor_name=cd['name'].upper())
            except Vendor.DoesNotExist:
                vendor = Vendor(
                    vendor_name=cd["name"].upper()
                )

                try:
                    vendor.save()
                except:
                    messages.error(request, "There was a problem saving this new vendor")
                    return redirect("add_inventory")
                else:
                    log_transaction('VAD', vendor.id)
                    messages.success(request, "Added a vendor named %s" % cd['name'].upper())
                    return redirect("add_inventory")
            else:
                messages.error(request, "There is a vendor with this name [%s] already" % cd['name'].upper())
                return redirect("add_inventory")

