# Tracking Plan — Piston Hub

The tracking plan is the contract between the business questions, the website code (dataLayer) and GTM/GA4.
Every event below is pushed by [`analytics.js`](https://github.com/Yuvrajbhagyedh/Piston-hub-Bike-accessory-website/blob/master/analytics.js) on the live site and uses
GA4's **recommended e-commerce event names**, so GA4's built-in Monetization reports work without custom mapping.

## Business questions → events

| Business question | Events that answer it |
|---|---|
| Where do shoppers drop out of the purchase journey? | `view_item_list` → `view_item` → `add_to_cart` → `begin_checkout` → `purchase` |
| Which products attract attention vs. actually sell? | `view_item`, `add_to_cart`, `purchase` (item-level) |
| Which collection pages (bike / brand) start buying journeys? | `view_item_list`, `select_item`, `select_content` |
| Which channels bring buyers, not just visitors? | All events + GA4 session source/medium |
| How much revenue is left in abandoned carts? | `view_cart`, `begin_checkout`, `remove_from_cart`, `purchase` |
| Is the site generating leads beyond online orders? | `generate_lead` |
| Are accounts helping conversion? | `sign_up`, `login` |

## Event specification

| Event | Fires when | Page(s) | Key parameters |
|---|---|---|---|
| `page_view` | Every page load | All | GA4 automatic (Enhanced Measurement) |
| `view_item_list` | A product grid is shown | Shop, 4 bike pages, 2 brand pages | `item_list_id`, `item_list_name`, `items[]` (with `index`) |
| `select_item` | A product card is clicked | Shop | `item_list_name`, `items[]` |
| `view_item` | Product detail page loads | 12 product pages | `currency`, `value`, `items[]` |
| `add_to_cart` | Add to Cart / Buy Now clicked | Product, list pages | `currency`, `value`, `items[]` (with `quantity`) |
| `remove_from_cart` | Item removed in cart | Cart | `currency`, `value`, `items[]` |
| `view_cart` | Cart page loads | Cart | `currency`, `value`, `items[]` |
| `begin_checkout` | Checkout loads with items in cart | Checkout | `currency`, `value`, `items[]` |
| `purchase` | Order confirmed | Checkout | `transaction_id`, `currency`, `value`, `shipping`, `items[]`, `shipping_city`, `order_type` |
| `sign_up` / `login` | Account created / logged in | Signup, Login | `method` |
| `generate_lead` | Contact form submitted | Contact | `form_name` |
| `select_content` | Bike/brand collection clicked on home page | Home | `content_type`, `content_id` |

### Item schema (inside `items[]`)

| Parameter | Example | Source |
|---|---|---|
| `item_id` | `axor-gloves` | product page slug — stable, never changes with renames |
| `item_name` | `Axor Gloves` | catalog |
| `item_brand` | `Axor` | catalog |
| `item_category` | `Gloves` | catalog (`Helmets` / `Gloves` / `Boots`) |
| `price` | `1799` | catalog, INR |
| `quantity` | `1` | cart |

All product data comes from **one catalog object** in `script.js`, so names, prices and categories are identical on every page and in every event.

## Example dataLayer push

```js
dataLayer.push({ ecommerce: null });           // clear the previous ecommerce object
dataLayer.push({
  event: "purchase",
  ecommerce: {
    transaction_id: "PH-100245",
    currency: "INR",
    value: 5298,
    shipping: 0,
    items: [
      { item_id: "axor-gloves", item_name: "Axor Gloves", item_brand: "Axor",
        item_category: "Gloves", price: 1799, quantity: 1 },
      { item_id: "apex-boots", item_name: "Apex Boots", item_brand: "Apex",
        item_category: "Boots", price: 3499, quantity: 1 }
    ]
  },
  shipping_city: "Bengaluru",
  order_type: "live"
});
```

## Privacy rules

- **No personal data is sent to GA4.** Name, email, phone, street address, PIN code and free-text form fields are never pushed to the dataLayer.
- `shipping_city` is the only location field — city-level, not personally identifying.
- Admin pages (`admin.html`, `admin-login.html`) do not load GTM at all, so internal staff activity never reaches GA4.
- Next step for production: Consent Mode v2 with a cookie banner (default `analytics_storage = denied` until accepted).

## GA4 configuration (recommended settings to apply in the property)

| Setting | Value |
|---|---|
| Key events (conversions) | `purchase`, `generate_lead`, `sign_up` |
| Custom dimensions (event scope) | `shipping_city`, `order_type`, `form_name` |
| Internal traffic filter | Exclude hostname `localhost` and office IP (see data-quality report) |
| Data retention | 14 months |
| Currency | INR |
