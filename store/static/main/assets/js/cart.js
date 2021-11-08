var updateBtns = document.getElementsByClassName("update-cart");
var plusBtn = document.getElementById("plus-btn");

for (var i = 0; i < updateBtns.length; i++) {
  updateBtns[i].addEventListener("click", function () {
    var productId = this.dataset.product;
    var action = this.dataset.action;
    var stock = this.dataset.stock;
    console.log("productID:", productId, "Action:", action, "Stock:", stock);
    console.log("User:", user);
    if (user == "AnonymousUser") {
      addCookieItem(productId, action, stock);
    } else {
      updateUserOrder(productId, action);
    }
  });
}

function addCookieItem(productId, action, stock) {
  console.log("User Unauthenticated");
  if (action == "add") {
    if (cart[productId] == undefined) {
      cart[productId] = { quantity: 1 };
    } else {
      if (+cart[productId]["quantity"] === stock) {
        plusBtn.disabled = true;
      } else {
        cart[productId]["quantity"] += 1;
      }
    }
  }
  if (action == "remove") {
    cart[productId]["quantity"] -= 1;

    if (cart[productId]["quantity"] <= 0) {
      console.log("Removed Item");
      delete cart[productId];
    }
  }
  console.log("Cart:", cart);
  document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
  location.reload();
}

function updateUserOrder(productId, action) {
  console.log("User is Logged in Sending Data..");

  var url = "/update_item/";

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      productId: productId,
      action: action,
    }),
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log("data:", data);
      location.reload();
    });
}
