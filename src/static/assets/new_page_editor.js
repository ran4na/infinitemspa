
function add_bbcode_tag(tagname) {
    const textbox = document.getElementById("new-page-textarea");
    var text_before = "";
    var text_after = "";

    const bbcodeTags = {
        pesterlog: { before: "[pesterlog]", after: "[/pesterlog]" },
        color: { before: "[color=#000000]", after: "[/color]" },
        italic: { before: "[i]", after: "[/i]" },
        bold: { before: "[b]", after: "[/b]" },
        underline: { before: "[u]", after: "[/u]" },
        list: { before: "[list]", after: "[/list]" },
        olist: { before: "[list=1]", after: "[/list]" },
        bullet: { before: "[*]", after: "" },
        url: { before: "[url=https://example.com]", after: "[/url]" },
        img: { before: "[img]", after: "[/img]"}
    };

    const tag = bbcodeTags[tagname];
    if (!tag) {
        return;
    }
    wrapBBcodeTag(textbox, tag.before, tag.after);
}

function wrapBBcodeTag(textarea, tag_start, tag_end) {
    const select_start = textarea.selectionStart;
    const select_end = textarea.selectionEnd;
    const selected = textarea.value.substring(select_start, select_end);
    const new_text = textarea.value.substring(0, select_start) + tag_start + selected + tag_end + textarea.value.substring(select_end);

    textarea.value = new_text
    textarea.selectionStart = select_start - tag_start.length;
    textarea.selectionEnd = select_end + tag_end.length;

}

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
