document.addEventListener("DOMContentLoaded", () => {

    const button = document.getElementById("trackBtn");

    button.addEventListener("click", async () => {
        console.log("🔥 Button clicked");

        let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        chrome.tabs.sendMessage(tab.id, { action: "GET_PRICE" }, (response) => {

            console.log("Response:", response);

            if (response && response.price) {
                alert("✅ Price: " + response.price);
            } else {
                alert("❌ Price not found");
            }

        });
    });

});