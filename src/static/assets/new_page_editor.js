


async function submitPage() {
    var pageForm = document.getElementById("new-page-form");
    const response = await fetch("/api/create_page", {
        method: "POST",
        body: new FormData(pageForm)
    });
    // check response. If success, redirect to the created page number.
    var json_data = await response.json();
    if(json_data["success"] != null) {
        // redirect to new page
        window.location.href = "/page/" + json_data["success"];
    }

    //  Otherwise, show error in #submit-error-msg
    var errorField = document.getElementById("submit-error-msg");
    if(json_data["error"] != null) {
        errorField.innerHTML = `Error: ${ json_data["error"] }`
    }
}
