function getPrice() {
    let priceElement =
        document.querySelector("[class*='price']") ||
        document.querySelector("[id*='price']");

    if (priceElement) {
        let priceText = priceElement.innerText;
        let price = priceText.replace(/[^0-9.]/g, "");
        return price;
    }
    return null;
}

// Send price to popup or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_PRICE") {
        const price = getPrice();
        sendResponse({ price: price });
    }
});