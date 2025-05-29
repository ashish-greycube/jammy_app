import frappe
import hashlib
import hmac
import json
import requests
import time
from frappe.utils import add_days, cint, now, today, cstr
from frappe.integrations.utils import create_request_log, make_get_request
from frappe.utils.response import json_handler

PER_PAGE = 200
ORDERS_API_ENDPOINT = "/api/orders"


def generate_signature(hmac_secret, method, path, params):
    hmac_secret = str.encode(hmac_secret)
    params = frappe._dict(params)
    signing_string = "&".join(
        [method, path] + [f"{k}={v}" for k, v in params.items()])

    hm = hmac.new(hmac_secret, signing_string.encode("utf-8"), hashlib.sha256)
    return hm.hexdigest()


def get_orders_url(from_date=None, page=1, per_page=50):

    settings = frappe.get_single("Jammy Settings")

    api_timestamp = int(time.time())

    # params["last_updated_at"] = "2023-08-11T06%3A40%3A25Z"
    last_updated_at = "{}T00%3A00%3A00Z".format(from_date)

    params = {
        "api_key": settings.shipping_easy_api_key,
        "api_timestamp": api_timestamp,
        "last_updated_at": last_updated_at,
        "page": page,
        "per_page": per_page,
        "status": "shipped",
    }

    signature = generate_signature(
        settings.shipping_easy_api_secret, "GET", ORDERS_API_ENDPOINT, params
    )

    query = "&".join([f"{k}={v}" for k, v in params.items()])

    return "{}{}?api_signature={}&{}".format(
        settings.shipping_easy_api_endpoint, ORDERS_API_ENDPOINT, signature, query
    )


@frappe.whitelist()
def sync_orders(from_date=None):
    frappe.msgprint("Enqueued Shipping Order sync from %s" % (from_date,))

    frappe.enqueue(
        _sync_orders,
        enqueue_after_commit=True,
        queue="long",
        from_date=from_date
    )


@frappe.whitelist()
def _sync_orders(from_date=None):
    if not cint(frappe.db.get_single_value("Jammy Settings", "is_syncing_enabled")):
        frappe.throw("Please enable syncing in Jammy Settings")

    if not from_date:
        seo = frappe.get_last_doc("Shipping Easy Order")
        updated_at = json.loads(seo.json_data or "{}").get("updated_at")
        if updated_at:
            from_date = updated_at.split("T")[0]

    if not from_date:
        from_date = add_days(today(), -1)

    error, response, all_orders, next_page = None, None, [], 1

    while True:
        try:
            url = get_orders_url(from_date, per_page=PER_PAGE, page=next_page)
            response = make_get_request(
                url, headers={"accept": "application/json"})
            all_orders.extend(response.get("orders", []))
            next_page = response.get("meta", {}).get("next_page")
            if not next_page:
                break
        except Exception as e:
            error = frappe.get_traceback()

    integration_request = create_request_log(
        {
            "url": url,
        },
        service_name="Shipping Easy: Fetch Orders",
        output=json.dumps(all_orders, default=json_handler),
        error=error,
        status="Completed" if not error else "Failed",
        is_remote_request=1,
    )

    for d in all_orders:
        make_shipping_easy_order(d)

    integration_request.add_comment(
        "Comment", text="Fetched {} orders".format(len(all_orders))
    )

    return integration_request.name


@frappe.whitelist()
def make_shipping_easy_order(order):
    uid = hashlib.sha256(json.dumps(order).encode("utf-8")).hexdigest()
    try:
        doc = frappe.get_doc(
            {
                "doctype": "Shipping Easy Order",
                "order_id": order["id"],
                "external_order_identifier": order["external_order_identifier"],
                "json_data": json.dumps(order),
                "fetched_on": now(),
                "status": "Pending",
                "uid": uid,
            }
        ).insert(ignore_permissions=True)
    except frappe.exceptions.UniqueValidationError as ex:
        print("skiping uniq:", order["external_order_identifier"])
        pass

    frappe.db.commit()


def fetch_orders(from_date=None):
    # page
    # per_page max 200
    # last_updated_at = 2017-05-24T19:38:25Z
    # status = "shipped", "cleared", "pending_shipment", "ready_for_shipment"

    if not from_date:
        from_date = add_days(today(), -1)

    settings = frappe.get_single("Jammy Settings")

    api_timestamp = int(time.time())
    path = "/api/orders"

    params = frappe._dict()
    params["api_key"] = settings.shipping_easy_api_key
    params["api_timestamp"] = api_timestamp
    # params["last_updated_at"] = "2023-08-11T06%3A40%3A25Z"
    params["last_updated_at"] = "{}T00%3A00%3A00Z".format(from_date)
    # params["per_page"] = 3
    params["status"] = "shipped"

    signature = generate_signature(
        settings.shipping_easy_api_secret, "GET", path, params
    )

    query = "&".join([f"{k}={v}" for k, v in params.items()])

    url = "{}{}?api_signature={}&{}".format(
        settings.shipping_easy_api_endpoint, path, signature, query
    )

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    return response.text


@frappe.whitelist()
def fetch_order(order_id="3415852983"):
    api_timestamp = int(time.time())
    path = f"/api/orders/{order_id}"
    settings = frappe.get_single("Jammy Settings")

    params = frappe._dict()
    params["api_key"] = settings.shipping_easy_api_key
    params["api_timestamp"] = api_timestamp
    signature = generate_signature(
        settings.shipping_easy_api_secret, "GET", path, params
    )

    query = "&".join([f"{k}={v}" for k, v in params.items()])

    url = "{}{}?api_signature={}&{}".format(
        settings.shipping_easy_api_endpoint, path, signature, query
    )

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    # return response.text
    make_shipping_easy_order(json.loads(response.text)["order"])


def notify_errors():
    """Cron. Runs Daily to notify of Error status Orders."""
    orders = frappe.get_all("Shipping Easy Order", {
                            "status": ["in", ["Error", "Batch Error"]]})
    if orders:
        if frappe.get_value("Notification", "Shipping Easy Failure Notification"):
            doc = frappe.get_doc("Shipping Easy Order", orders[0].name)
            frappe.get_doc(
                "Notification", "Shipping Easy Failure Notification"
            ).send_an_email(doc, {"count": len(orders)})
