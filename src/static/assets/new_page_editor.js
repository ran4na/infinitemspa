
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

function openTegaki() {
    Tegaki.open({
        // when the user clicks on Finish
        onDone: function() {          
          var data_url = Tegaki.flatten().toDataURL('image/png')
          setFiletoDataURL(data_url, "tegaki.png");
        },
        // when the user clicks on Cancel
        onCancel: function() { console.log('Closing...')},
        
        // initial canvas size
        width: 650,
        height: 450
      });
}

// Embed tegaki image data URL to file chooser
async function setFiletoDataURL(url, filename) {
    // Fetch from URL
    const response = await fetch(url);
    const blob = await response.blob();
    
    // Create new ""File"" from the url blob
    const file = new File([blob], filename);
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);

    const fileInput = document.getElementById("file_upload");
    fileInput.files = dataTransfer.files;

    // Fire onchange to update preview
    const changeEvent = new Event('change');
    fileInput.dispatchEvent(changeEvent);
}

function loadFile(event) {
    var preview_element = document.getElementById("output-preview");
    preview_element.src = URL.createObjectURL(event.target.files[0]);
    preview_element.onload = function() {
        URL.revokeObjectURL(output.src);
    }
}