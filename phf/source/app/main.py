import base64
import hashlib
import secrets
import socket
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Any

from fastapi.responses import RedirectResponse
import jwt
from jwt import algorithms as jwt_algo
from fastapi import (
    BackgroundTasks,
    Cookie,
    Depends,
    FastAPI,
    Form,
    Request,
    status,
    Query,
)
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import mimetypes

# make some hack
jwt_algo.NoneAlgorithm.prepare_key = lambda *_: None  # type: ignore
jwt_algo.NoneAlgorithm.verify = lambda *_: True  # type: ignore


templates = Jinja2Templates("templates")

app = FastAPI(openapi_url=None)


class UserRole(Enum):
    MERCHANT = 0
    CUSTOMER = 1


class UserLoginForm(BaseModel):
    username: str
    password: str


class UserModel(BaseModel):
    username: str
    password: str = Field(exclude=True)
    name: str


class User(UserModel):
    role: UserRole
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class ItemModel(BaseModel):
    name: str
    value: float
    discount: float = 1.0
    cost_estimate_script: str
    cook_script: str
    image: str | None = None


class Item(ItemModel):
    merchant_id: uuid.UUID
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class DeliveryInfo(BaseModel):
    address: str
    name: str
    phone: str


class OrderModel(BaseModel):
    discount: bool
    delivery: DeliveryInfo


class TraceInfo(BaseModel):
    type: str
    detail: str


class Order(OrderModel):
    item: Item
    cost: float

    estimated_time: datetime | None = None

    trace: list[TraceInfo] = Field(default_factory=list[TraceInfo])
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class CustomerInfo(BaseModel):
    balance: float = 0
    orders: list[Order] = Field(default_factory=list[Order])


COST_ESTIMATE_SCRIPT = "(1145, 100)"
COOK_SCRIPT = r'f"{order.item.name}\n联系人: {order.delivery.name} {order.delivery.phone}\n地址: {order.delivery.address}\n".encode("utf-8")'


XIBEI_USER = User(
    username="xibei",
    password=secrets.token_hex(31),
    name="西贝莜面村",
    role=UserRole.MERCHANT,
)  # invalid sha256.
MXBC_USER = User(
    username="mxbc",
    password=secrets.token_hex(31),
    name="蜜雪冰城",
    role=UserRole.MERCHANT,
)  # invalid sha256.
ZAKO_USER = User(
    username="zako",
    password=hashlib.sha256(b"zakozako").hexdigest(),
    name="杂鱼",
    role=UserRole.CUSTOMER,
)

users: list[User] = [XIBEI_USER, MXBC_USER, ZAKO_USER]

customers_info: dict[uuid.UUID, CustomerInfo] = {ZAKO_USER.id: CustomerInfo(balance=100)}


def file_base64_encode(path: str, *, mimetype: str | None = None) -> str:
    if mimetype is None:
        mimetype, _ = mimetypes.guess_type(path)

    if mimetype is None:
        raise ValueError

    with open(path, "rb") as fp:
        encoded = base64.b64encode(fp.read()).decode()

    return f"data:{mimetype};base64,{encoded}"


items: list[Item] = [
    Item(
        name="罗永浩同款套餐",
        value=663,
        discount=0.85,
        cost_estimate_script=COST_ESTIMATE_SCRIPT,
        cook_script=COOK_SCRIPT,
        merchant_id=XIBEI_USER.id,
        image=file_base64_encode("assets/xibei.webp", mimetype="image/webp"),
    ),
    Item(
        name="糯香柠檬茶",
        value=3.9,
        discount=0.95,
        cost_estimate_script=COST_ESTIMATE_SCRIPT,
        cook_script=COOK_SCRIPT,
        merchant_id=MXBC_USER.id,
        image=file_base64_encode("assets/lemon.webp", mimetype="image/webp"),
    ),
    Item(
        name="棒打今日橙",
        value=4.9,
        discount=0.95,
        cost_estimate_script=COST_ESTIMATE_SCRIPT,
        cook_script=COOK_SCRIPT,
        merchant_id=MXBC_USER.id,
        image=file_base64_encode("assets/orange.webp", mimetype="image/webp"),
    ),
]


JWT_KEY = secrets.token_bytes()


class Unauthorized(Exception):
    pass


class NotFound(Exception):
    pass


def user_dep(token: Annotated[str | None, Cookie()] = None) -> User:
    if token is None:
        raise Unauthorized

    try:
        # accept all algos
        payload = jwt.decode(  # type: ignore
            token, JWT_KEY, algorithms=list(jwt_algo.get_default_algorithms().keys())
        )
    except jwt.InvalidSignatureError as ex:
        raise Unauthorized from ex

    if (user_id := payload.get("sub")) is None:
        raise Unauthorized

    user_id = uuid.UUID(user_id)
    user = next((user for user in users if user.id == user_id), None)

    if user is None:
        raise Unauthorized

    return user


UserDep = Annotated[User, Depends(user_dep)]


def role_restricted_user_dep(role: UserRole) -> Any:
    def dependency(user: UserDep) -> User:
        if user.role != role:
            raise Unauthorized

        return user

    return Depends(dependency)


CustomerDep = Annotated[User, role_restricted_user_dep(UserRole.CUSTOMER)]
MerchantDep = Annotated[User, role_restricted_user_dep(UserRole.MERCHANT)]


def customer_info_dep(customer: CustomerDep) -> CustomerInfo:
    return customers_info.setdefault(customer.id, CustomerInfo())


CustomerInfoDep = Annotated[CustomerInfo, Depends(customer_info_dep)]


def item_dep(item_id: uuid.UUID) -> Item:
    item = next((item for item in items if item.id == item_id), None)

    if item is None:
        raise NotFound

    return item


ItemDep = Annotated[Item, Depends(item_dep)]


def run_script(script: str, variables: dict[str, Any] | None = None) -> Any:
    if variables is None:
        variables = {}
    else:
        variables = variables.copy()

    variables["__builtins__"] = None
    return eval(script, variables, variables)


def cook_and_deliver(order: Order) -> None:
    try:
        order.trace.append(TraceInfo(type="进行中", detail="打印小票中"))
        ip, port = order.delivery.address.split(":")
        port = int(port)

        order.trace.append(TraceInfo(type="进行中", detail="商家正在备餐"))
        result: bytes = run_script(order.item.cook_script, {"order": order})

        order.trace.append(TraceInfo(type="进行中", detail="骑手正在赶往商家"))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        order.trace.append(TraceInfo(type="进行中", detail="骑手正在配送"))
        sock.connect((ip, port))
        sock.sendall(result)

        order.trace.append(TraceInfo(type="已完成", detail="商品已送达"))
    except Exception as ex:
        order.trace.append(TraceInfo(type="配送失败", detail=str(ex)))


def humanize_time(secs: float) -> str:
    if secs < 60:
        return "1分钟内"
    else:
        minutes = round(secs / 60)
        return f"{minutes}分钟"


def humanize_distance(meters: float) -> str:
    if meters < 1000:
        return f"{meters}m"
    else:
        kilos = round(meters / 1000, 1)
        return f"{kilos}km"


@app.exception_handler(NotFound)
async def not_found_hanlder(request: Request, exc: Unauthorized) -> RedirectResponse:
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.exception_handler(Unauthorized)
async def unauthorized_hanlder(request: Request, exc: Unauthorized) -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/")
def homepage(request: Request, user: UserDep) -> Any:
    if user.role == UserRole.CUSTOMER:
        merchants = {user.id: user for user in users if user.role == UserRole.MERCHANT}
        return templates.TemplateResponse(
            request, "index.html", {"items": items, "merchants": merchants}
        )
    elif user.role == UserRole.MERCHANT:
        return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)
    else:
        assert False, "never branch."


@app.get("/items/{item_id}")
def item_page(request: Request, item: ItemDep) -> Any:
    merchant = next(user for user in users if user.id == item.merchant_id)
    distance, cost_secs = run_script(item.cost_estimate_script, {"item": item})
    cost = humanize_time(cost_secs)
    distance = humanize_distance(distance)
    return templates.TemplateResponse(
        request,
        "item.html",
        {"item": item, "merchant": merchant, "distance": distance, "cost": cost},
    )


@app.get("/orders")
def orders_page(request: Request, info: CustomerInfoDep) -> Any:
    merchants = {user.id: user for user in users if user.role == UserRole.MERCHANT}

    return templates.TemplateResponse(
        request, "orders.html", {"orders": info.orders, "merchants": merchants}
    )


@app.get("/order/{item_id}")
def order_page(
    request: Request,
    customer_info: CustomerInfoDep,
    item: ItemDep,
    alert: str | None = None,
    discount: bool = False,
    delivery: Annotated[str | None, Query()] = None,
) -> Any:
    merchant = next(user for user in users if user.id == item.merchant_id)
    _, cost_secs = run_script(item.cost_estimate_script, {"item": item})
    cost = humanize_time(cost_secs)

    if delivery:
        delivery_info = DeliveryInfo.model_validate_json(delivery)
    else:
        delivery_info = None

    return templates.TemplateResponse(
        request,
        "order.html",
        {
            "item": item,
            "merchant": merchant,
            "cost": cost,
            "discount": discount,
            "alert": alert,
            "delivery": delivery_info,
            "customer": customer_info,
        },
    )


@app.get("/address/{item_id}")
def address_page(
    request: Request,
    customer: CustomerDep,
    item: ItemDep,
    discount: bool = False,
) -> Any:
    return templates.TemplateResponse(
        request,
        "address.html",
        {
            "item": item,
            "discount": discount,
        },
    )


@app.get("/login")
def login_page(request: Request) -> Any:
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
def login(request: Request, form: Annotated[UserLoginForm, Form()]) -> Any:
    user = next((user for user in users if user.username == form.username), None)

    if user is None or hashlib.sha256(form.password.encode()).hexdigest() != user.password:
        return templates.TemplateResponse(request, "login.html", {"failed": True})

    payload = {"sub": str(user.id)}
    token = jwt.encode(payload, JWT_KEY, "HS256")  # type: ignore

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("token", token)
    return response


@app.post("/order/{item_id}")
def order(
    info: CustomerInfoDep,
    item: ItemDep,
    background_tasks: BackgroundTasks,
    discount: bool,
    delivery: Annotated[str, Query()],
) -> RedirectResponse:
    value = round(item.value * item.discount, 2) if discount else item.value

    if info.balance < value:
        response = RedirectResponse(
            f"/order/{item.id}?discount={discount}&alert=余额不足",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        return response

    info.balance -= value

    delivery_info = DeliveryInfo.model_validate_json(delivery)
    order = Order(discount=discount, delivery=delivery_info, item=item, cost=value)
    info.orders.append(order)

    _, estimated_secs = run_script(item.cost_estimate_script, {"item": item})
    estimated_time = datetime.now() + timedelta(seconds=estimated_secs)

    order.estimated_time = estimated_time

    background_tasks.add_task(cook_and_deliver, order)

    response = RedirectResponse(f"/", status_code=status.HTTP_303_SEE_OTHER)
    return response


@app.get("/admin")
def admin_homepage(request: Request, user: MerchantDep) -> Any:
    merchant_items = [item for item in items if item.merchant_id == user.id]
    return templates.TemplateResponse(request, "admin/index.html", {"items": merchant_items})


@app.get("/admin/items/{item_id}")
def item_update_page(request: Request, user: MerchantDep, item: ItemDep) -> Any:
    return templates.TemplateResponse(request, "admin/item.html", {"item": item})


@app.post("/admin/items/{item_id}")
def item_update(
    request: Request, user: MerchantDep, item: ItemDep, form: Annotated[ItemModel, Form()]
) -> RedirectResponse:
    for name in ItemModel.model_fields:
        value = getattr(form, name)
        setattr(item, name, value)

    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)
