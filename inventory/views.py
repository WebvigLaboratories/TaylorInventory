from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

from models import *
from forms import *

import datetime

HISTORY_LOG = "logs/history.log"

def logHistory(message):
    now = datetime.datetime.now()
    now = now.strftime("%m/%d/%Y %H:%M:%S")

    fLog = open(HISTORY_LOG, "a")

    fLog.writelines("%s - %s\n" % (now, message))

    fLog.close()

    return True


@login_required
def showHistory(request):
    dReturn = {}

    now = datetime.date.today()
    find_day = now - datetime.timedelta(days=90)

    # Gather log
    log = HISTORY_LOG
    lHistory = []
    # Read the log file - get the lines for the specified days
    fLog = open(log, "r")

    for line in fLog.readlines():
        if line != "":
            linemonth = line.split("/")[0]
            lineday = line.split("/")[1]
            lineyear = line.split("/")[2][0:4]

            # Added to deal with the end of year sorting issues
            linetext = line.split("-",1)[1]
            linedate = datetime.date(int(lineyear), int(linemonth), int(lineday))

            if linedate > find_day:
                lHistory.append("%s/%s/%s - %s" % (lineyear,linemonth,lineday,linetext))
                #lHistory.append(line)

    fLog.close()
    lHistory = sorted(lHistory, reverse=True)
    dReturn['lHistory'] = lHistory

    return render(request, "inventory/history.html", dReturn)


@login_required
def vendorAdd(request):
    dReturn = {}

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
                    vendor_name = cd["name"].upper()
                )

                try:
                    vendor.save()
                except:
                    messages.error(request, "There was a problem saving this new vendor")
                    return redirect("add_inventory")
                else:
                    logHistory("%s - Added vendor [%s]" % (request.user.username, cd['name'].upper()))
                    messages.success(request, "Added a vendor named %s" % cd['name'].upper())
                    return redirect("add_inventory")
            else:
                messages.error(request, "There is a vendor with this name [%s] already" % cd['name'].upper())
                return redirect("add_inventory")


@login_required
def inventoryAdd(request):
    # TODO - Add functionality to add a new vendor on the add inventory item page
    dReturn = {}
    dReturn['title'] = "Add New Inventory Item"

    if request.method == 'POST':
        # check response
        form = InventoryForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            vendor = cd['vendor']

            item = Item(
                item_number = cd["itemnumber"],
                description = cd["description"],
                vendor_name = vendor,
                quantity    = cd["quantity"],
                cost        = cd["cost"],
                hidden      = 0
            )

            try:
                item.save()
            except:
                messages.error(request, "There was an error saving this new item")
                return redirect("list_inventory")
            else:
                logHistory("%s - Added new inventory item [%s]" % (request.user.username, cd['description']))
                messages.success(request, "Saved new item [%s]" % cd['itemnumber'])
                return redirect("list_inventory")

        else:
            dReturn['form'] = form
    else:
        form = InventoryForm()
        dReturn['form'] = form
        dReturn['vendorform'] = VendorForm()

    return render(request, "inventory/add.html", dReturn)


@login_required
def inventoryEdit(request, itemid):
    dReturn = {}

    try:
        item = Item.objects.get(id=itemid)
    except Item.DoesNotExist:
        messages.error(request, "The item searched does not exist")
        return redirect("list_inventory")

    dReturn['title'] = "Edit %s" % item.item_number

    if request.method == 'POST':
        # check response
        form = InventoryForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            lChanged = []
            dChanged = {}

            # FIXME - Add cost error checking to form
            if item.item_number != cd['itemnumber']:
                item.item_number = cd['itemnumber']
                lChanged.append("Item Number|%s" % cd['itemnumber'])

            if item.description != cd['description']:
                item.description    = cd['description']
                lChanged.append("Description|%s" % cd['description'])

            if str(item.quantity) != cd['quantity']:
                item.quantity       = cd['quantity']
                lChanged.append("Quantity|%s" % cd['quantity'])

            if str(item.cost) != cd['cost']:
                item.cost           = cd['cost']
                lChanged.append("Cost|%s" % cd['cost'])

            if item.vendor_name != cd['vendor']:
                item.vendor_name    = cd['vendor']
                lChanged.append("Vendor|%s" % cd['vendor'].vendor_name)

            if item.hidden != cd['hidden']:
                item.hidden = cd['hidden']
                lChanged.append("Deleted Flag|%s" % cd['hidden'] )

            try:
                item.save()
            except:
                messages.error(request, "There was an error saving these changes")
                return redirect("list_inventory")
                # TODO - redirect this back to edit form with old values
            else:
                for change in lChanged:
                    logHistory("%s - Edited the item [%s] by changing [%s] to [%s]" % (request.user.username, cd['description'],
                                                                                       change.split("|")[0], change.split("|")[1]))
                    messages.success(request, "Saved changes to %s" % change.split("|")[0])

                return redirect("list_inventory")

        else:
            dReturn['form'] = form
    else:
        form = InventoryForm(initial={
            "itemnumber"    : item.item_number,
            "description"   : item.description,
            "vendor"        : item.vendor_name_id,
            "quantity"      : item.quantity,
            "cost"          : item.cost,
            "hidden"        : item.hidden,
        })

        dReturn['form'] = form

    return render(request, "inventory/edit.html", dReturn)


@login_required
def inventoryDelete(request, itemid):
    dReturn = {}

    try:
        item = Item.objects.get(id=itemid)
    except Item.DoesNotExist:
        messages.error(request, "The item searched does not exist")
        return redirect("list_inventory")

    #item.hidden = True
    description = item.description
    itemnumber = item.item_number

    try:
        #item.save()
        item.delete()
    except:
        messages.error(request, "There was an error deleting this item")
    else:
        logHistory("%s - Deleted the item [%s]" % (request.user.username, description))
        messages.success(request, "Deleted item [%s]" % itemnumber)

    return redirect("list_inventory")


@login_required
def inventoryList(request, showdeleted=False):
    dReturn = {}

    if showdeleted:
        dReturn['title'] = "Inventory Administration - Showing Items Marked Deleted"
    else:
        dReturn['title'] = "Inventory Administration"

    #TODO - Switch the show deleted button on the list.html page to a toggle button - see twitter bootstrap
    if request.method == 'POST':
        if 'filter' in request.POST and request.POST['filter']:
            search = request.POST['filter']
            dReturn['search'] = search

            if showdeleted:
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
                    items = Item.objects.filter(description__icontains=search).exclude(hidden=1).order_by("item_number")

                if len(items) == 0:
                    # Check the vendors
                    items = Item.objects.filter(vendor_name__vendor_name__icontains=search).exclude(hidden=1).order_by("item_number")

                if len(items) == 0:
                    messages.info(request, "Could not find anything that contains your search phrase [%s]" % search)
                    items = ""

            dReturn['items'] = items

    else:

        if showdeleted:
            # Return a list of all items including deleted items
            items = Item.objects.all().order_by("item_number")
        else:
            # Return a list of all items excluding deleted items
            items = Item.objects.all().exclude(hidden=1).order_by("item_number")

    dReturn['items'] = items

    return render(request, "inventory/list.html", dReturn)


@login_required
def receiveInventory(request):
    dReturn = {}
    dReturn['title'] = "Record Received Items"
    dReturn['buttonaction'] = "Receive"

    if request.method == 'POST':
        # check response
        form = QuantityForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            item = cd['item']

            item.quantity = item.quantity + cd['quantity']

            try:
                item.save()
            except:
                messages.error(request, "There was a problem updating the quantity for item [%s]" % item.description)
            else:
                logHistory("%s - Recieved %s items for [%s - %s] - You now have a quantity of %s" % (request.user.username, cd['quantity'],
                                                                                                     item.item_number, item.description, item.quantity))
                messages.success(request, "Received %s items for [%s - %s] - You now have a quantity of %s" % (cd['quantity'],
                                                                                                               item.item_number, item.description, item.quantity))

            return redirect("receive_inventory")

        else:
            dReturn['form'] = form
    else:
        form = QuantityForm(initial={
            "quantity"    : 0
        })

        dReturn['form'] = form

    return render(request, "inventory/shipreceive.html", dReturn)


@login_required
def shipInventory(request):
    dReturn = {}
    dReturn['title'] = "Record Shipped Items"
    dReturn['buttonaction'] = "Ship"

    if request.method == 'POST':
        # check response
        form = QuantityForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            item = cd['item']

            # Check item quantity to see if they have enough items to ship
            if item.quantity < cd['quantity']:
                messages.error(request, "You do not have enough items in your inventory to ship the quantity [%s] you entered" % cd['quantity'])
                messages.info(request, "You have a quantity of %s   items for %s" % (item.quantity, item.description))
            else:
                item.quantity = item.quantity - cd['quantity']

                try:
                    item.save()
                except:
                    messages.error(request, "There was a problem updating the quantity for item [%s]" % item.description)
                else:
                    logHistory("%s - Shipped %s items for [%s - %s] - You now have a quantity of %s" % (request.user.username, cd['quantity'],
                                                                                                        item.item_number, item.description, item.quantity))
                    messages.success(request, "Shipped %s items for [%s - %s] - You now have a quantity of %s" % (cd['quantity'],
                                                                                                                  item.item_number, item.description, item.quantity))

            return redirect("ship_inventory")

        else:
            dReturn['form'] = form
    else:
        form = QuantityForm(initial={
            "quantity"    : 0,
        })

        dReturn['form'] = form

    return render(request, "inventory/shipreceive.html", dReturn)


@login_required
def reports(request):
    dReturn = {}
    dReturn['title'] = "Generate Reports"

    if request.method == 'POST':
        if 'filter' in request.POST and request.POST['filter']:
            search = request.POST['filter']

            # Check the item number
            items = Item.objects.filter(item_number__icontains=search).exclude(hidden=1).order_by("item_number")

            if len(items) == 0:
                # Check the description
                items = Item.objects.filter(description__icontains=search).exclude(hidden=1).order_by("item_number")

            if len(items) == 0:
                # Check the vendors
                items = Item.objects.filter(vendor_name__vendor_name__icontains=search).exclude(hidden=1).order_by("item_number")

            if len(items) == 0:
                messages.info(request, "Could not find anything that contains your search phrase [%s]" % search)
                items = ""

            dReturn['items'] = items

    else:
        # Return a list of all the items
        items = Item.objects.all().exclude(hidden=1).order_by("item_number")

    dReturn['items'] = items

    #Calculate Grand Total for requested entry
    grandtotal = 0
    for item in items:
        itemtotal = item.quantity * item.cost
        grandtotal = grandtotal + itemtotal

    dReturn['grandtotal'] = float(grandtotal)

    return render(request, "inventory/reports.html", dReturn)


def accountLogin(request):
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


def accountLogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")

    return redirect(reverse("home"))


@login_required
def index(request):
    dReturn = {}
    dReturn['title'] = "Inventory Tracking"

    return render(request, 'inventory/index.html', dReturn)