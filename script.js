document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // CART
    // =========================

    let cart = [];

    const cartCount = document.getElementById("cart-count");
    const cartItems = document.getElementById("cart-items");
    const totalItems = document.getElementById("total-items");
    const cartSubtotal = document.getElementById("cart-subtotal");
    const cartTotal = document.getElementById("cart-total");


    // =========================
    // ADD TO CART
    // =========================

    const addButtons = document.querySelectorAll(".add-cart");

    console.log("Add buttons:", addButtons.length);


    addButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const productCard =
                button.closest(".product-card");

            if (!productCard) {
                console.error("Product card not found");
                return;
            }


            const name =
                productCard.querySelector("h3").textContent.trim();


            const priceText =
                productCard.querySelector(".price").textContent.trim();


            const price =
                parseInt(
                    priceText.replace(/[₹,\s]/g, ""),
                    10
                );


            if (isNaN(price)) {
                console.error("Invalid price:", priceText);
                return;
            }


            // Check existing product

            const existing =
                cart.find(function (item) {

                    return item.name === name;

                });


            if (existing) {

                existing.quantity++;

            } else {

                cart.push({

                    name: name,

                    price: price,

                    quantity: 1

                });

            }


            updateCart();


            button.textContent = "Added ✓";


            setTimeout(function () {

                button.textContent = "Add to Cart";

            }, 800);

        });

    });



    // =========================
    // UPDATE CART
    // =========================

    function updateCart() {

        let items = 0;

        let total = 0;


        cart.forEach(function (item) {

            items += item.quantity;

            total +=
                item.price * item.quantity;

        });


        // Navbar

        cartCount.textContent = items;


        // Summary

        totalItems.textContent = items;

        cartSubtotal.textContent = total;

        cartTotal.textContent = total;


        // Empty cart

        if (cart.length === 0) {

            cartItems.innerHTML = `
                <p id="empty-cart">
                    Your cart is empty 😔
                </p>
            `;

            return;

        }


        // Display cart

        cartItems.innerHTML = "";


        cart.forEach(function (item, index) {

            const div =
                document.createElement("div");

            div.className = "cart-item";


            div.innerHTML = `

                <div class="cart-product-info">

                    <h3>${item.name}</h3>

                    <p>₹${item.price}</p>

                </div>


                <div class="quantity-control">

                    <button
                        type="button"
                        onclick="decreaseQuantity(${index})">

                        −

                    </button>


                    <span>
                        ${item.quantity}
                    </span>


                    <button
                        type="button"
                        onclick="increaseQuantity(${index})">

                        +

                    </button>

                </div>


                <div class="cart-product-total">

                    <strong>
                        ₹${item.price * item.quantity}
                    </strong>


                    <button
                        type="button"
                        class="remove-btn"
                        onclick="removeFromCart(${index})">

                        Remove

                    </button>

                </div>

            `;


            cartItems.appendChild(div);

        });

    }



    // =========================
    // INCREASE
    // =========================

    window.increaseQuantity = function (index) {

        if (cart[index]) {

            cart[index].quantity++;

            updateCart();

        }

    };



    // =========================
    // DECREASE
    // =========================

    window.decreaseQuantity = function (index) {

        if (!cart[index]) {
            return;
        }


        cart[index].quantity--;


        if (cart[index].quantity <= 0) {

            cart.splice(index, 1);

        }


        updateCart();

    };



    // =========================
    // REMOVE
    // =========================

    window.removeFromCart = function (index) {

        if (!cart[index]) {
            return;
        }


        cart.splice(index, 1);


        updateCart();

    };



    // =========================
    // PRODUCT FILTER
    // =========================

    const filterButtons =
        document.querySelectorAll(".filter-btn");


    const products =
        document.querySelectorAll(".product-card");


    console.log(
        "Filter buttons:",
        filterButtons.length
    );


    filterButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const category =
                button.getAttribute("data-category");


            // Active button

            filterButtons.forEach(function (btn) {

                btn.classList.remove("active");

            });


            button.classList.add("active");


            // Filter products

            products.forEach(function (product) {

                const productCategory =
                    product.getAttribute("data-category");


                if (
                    category === "all" ||
                    productCategory === category
                ) {

                    product.style.display = "";

                } else {

                    product.style.display = "none";

                }

            });

        });

    });



    // =========================
    // CATEGORY EXPLORE
    // =========================

    window.exploreCategory = function (category) {

        console.log(
            "Explore:",
            category
        );


        const filterButton =
            document.querySelector(
                '.filter-btn[data-category="' +
                category +
                '"]'
            );


        if (filterButton) {

            filterButton.click();

        }


        const productsSection =
            document.getElementById("products");


        if (productsSection) {

            setTimeout(function () {

                productsSection.scrollIntoView({

                    behavior: "smooth",

                    block: "start"

                });

            }, 100);

        }

    };



    // =========================
    // CHECKOUT
    // =========================

 window.checkout = function () {

    if (cart.length === 0) {

        alert(
            "Your cart is empty! Please add a product first."
        );

        return;

    }

    // Save cart temporarily
    localStorage.setItem(
        "foodhubCart",
        JSON.stringify(cart)
    );

    // Open checkout page
    window.location.href = "/checkout";

};



    // =========================
    // INITIAL CART
    // =========================

    updateCart();


    console.log(
        "FoodHub loaded successfully ✅"
    );

});