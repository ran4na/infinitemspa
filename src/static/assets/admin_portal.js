document.addEventListener("DOMContentLoaded", populatePageTable);
document.addEventListener("DOMContentLoaded", populateBanTable);
document.addEventListener("DOMContentLoaded", populateImageTable);
document.addEventListener("DOMContentLoaded", getLockStatus);

// Gets page listand populates table
async function populatePageTable() {
    const pages = await fetch('/api/get_page_list_admin', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })

    var json_data = await pages.json();
    if (json_data["error"] != null) {
        // redirect to new page
        return;
    }

    var pageTable = document.getElementById("page-table");
    console.log("Populating page tables.")
    pageTable.innerHTML = ""; // Clear the table before populating it
    pageTable.innerHTML += `<tr>
                <th>Page #</th>
                <th>Page title</th>
                <th>Panel img ID</th>
                <th>Panel img filename</th>
                <th>Page text</th>
                <th>Uploader #</th>
                <th>Deleted</th>
                <th></th>
                <th></th>
            </tr>`;
    
    for (var i = 0; i < json_data.length; i++) {
        var page = json_data[i];
        
        var row = document.createElement("tr");
        row.innerHTML = `<td>${page["page_num"]}</td>
                         <td>${page["page_title"]}</td>
                         <td>${page["panel_file_id"]}</td>
                         <td>${page["panel_filename"]}</td>
                         <td>${page["page_text"].substring(0, 20)}...</td>
                         <td>${page["page_uploader"]}</td>
                         <td>${page["deleted"]}</td>
                         <td><button onclick="softDelPage(${page["page_num"]})">Soft delete</button></td>
                         <td><button onclick="banUser('${page["page_uploader"]}')">Ban uploader</button></td>`;
        pageTable.appendChild(row);
    }

}

// Gets ban list and populates table
async function populateBanTable() {
    const bans = await fetch('/api/get_banned_users', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })

    var json_data = await bans.json();
    ban_header_string = `<tr>
                <th>Ban #</th>
                <th>IP hash</th>
                <th></th>
            </tr>`;
    if (json_data["error"] != null) {
        // redirect to new page
        var banTable = document.getElementById("ban-table");
        banTable.innerHTML = ""; // Clear the table before populating it
        banTable.innerHTML += ban_header_string;
        return;
    }

    var banTable = document.getElementById("ban-table");
    console.log("Populating ban tables.")
    banTable.innerHTML = ""; // Clear the table before populating it
    banTable.innerHTML += ban_header_string;
    for (var i = 0; i < json_data.length; i++) {
        var ban = json_data[i];
        
        var row = document.createElement("tr");
        row.innerHTML = `<td>${ban["id"]}</td>
                         <td>${ban["ip_hash"]}</td>
                         <td><button onclick="unbanUser(${ban["id"]})">Unban</button></td>`;
        banTable.appendChild(row);
    }

}

// Gets image list and populates table
async function populateImageTable() {
    const images = await fetch('/api/get_image_list', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })

    var json_data = await images.json();
    img_header_string = `<tr>
                <th>Image #</th>
                <th>Filename</th>
                <th>Hash</th>
            </tr>`

    if (json_data["error"] != null) {
        // redirect to new page
        var imgTable = document.getElementById("img-table");
        imgTable.innerHTML = ""; // Clear the table before populating it
        imgTable.innerHTML += img_header_string;
        return;
    }

    var imgTable = document.getElementById("img-table");
    console.log("Populating image tables.")
    imgTable.innerHTML = ""; // Clear the table before populating it
    imgTable.innerHTML += img_header_string;
    for (var i = 0; i < json_data.length; i++) {
        var img = json_data[i];
        
        var row = document.createElement("tr");
        row.innerHTML = `<td>${img["id"]}</td>
                         <td>${img["image_filename"]}</td>
                         <td>${img["image_hash"]}</td>
                         <td><button onclick="softDelImage(${img["id"]})">Soft delete</button></td>`;
        imgTable.appendChild(row);
    }

}

async function softDelPage(page_number) {
    if (confirm(`Soft delete page ${page_number}?`)) {
        const formData = new URLSearchParams();
        formData.append("page_num", page_number);

        const res = await fetch('/api/soft_delete_page', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });

        const json_data = await res.json();
        if (json_data.error != null) {
            alert("Error: " + json_data.error);
        } else if (json_data.success != null) {
            alert("Page " + page_number + " soft-deleted successfully.");
            await populatePageTable(); // Refresh the table after deletion
        }
    }
}

async function softDelImage(image_id) {
    if (confirm(`Soft delete image ${image_id}?`)) {
        const formData = new URLSearchParams();
        formData.append("image_id", image_id);

        const res = await fetch('/api/soft_delete_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });

        const json_data = await res.json();
        if (json_data.error != null) {
            alert("Error: " + json_data.error);
        } else if (json_data.success != null) {
            alert("Image " + image_id + " soft-deleted successfully.");
            await populateImageTable(); // Refresh the table after deletion
        }
    }
}

async function banUser(upload_hash) {
    if (confirm(`Ban user ${upload_hash}?`)) {
        const formData = new URLSearchParams();
        formData.append("uploader_ip_hash", upload_hash);

        const res = await fetch('/api/ban_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });

        const json_data = await res.json();
        if (json_data.error != null) {
            alert("Error: " + json_data.error);
        } else if (json_data.success != null) {
            alert(json_data.success);
            await populateBanTable();
        }
    }
}

async function unbanUser(ban_id) {
    if (confirm(`Remove ban id ${ban_id}?`)) {
        const formData = new URLSearchParams();
        formData.append("ban_id", ban_id);

        const res = await fetch('/api/unban_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });

        const json_data = await res.json();
        if (json_data.error != null) {
            alert("Error: " + json_data.error);
        } else if (json_data.success != null) {
            alert(json_data.success);
            await populateBanTable();
        }
    }
}

async function toggleLock() {
    const toggleLock = await fetch('/api/toggle_upload_lock', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    var json_data = await toggleLock.json();
    if (json_data["error"] != null || json_data == null) {
        // redirect to new page
        return;
    }
    var status = document.getElementById("upload-status");

    var lockButton = document.getElementById("lock-button");
    if (json_data["locked"] == "True") {
        lockButton.innerHTML = "Unlock uploads";
        status.innerHTML = "Uploads: Locked";
        
    } else {
        lockButton.innerHTML = "Lock uploads";
        status.innerHTML = "Uploads: Unlocked";
    }
}

async function getLockStatus() {
    const toggleLock = await fetch('/api/get_lock_status', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    var json_data = await toggleLock.json();
    if (json_data["error"] != null || json_data == null) {
        // redirect to new page
        return;
    }
    var status = document.getElementById("upload-status");
    var lockButton = document.getElementById("lock-button");

    if (json_data["locked"] == "True") {
        lockButton.innerHTML = "Unlock uploads";
        status.innerHTML = "Uploads: Locked";
        
    } else {
        lockButton.innerHTML = "Lock uploads";
        status.innerHTML = "Uploads: Unlocked";
    }
}