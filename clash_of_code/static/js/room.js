const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode(`ace/mode/${roomData.languageMode}`);
editor.setOptions({
    fontSize: "14px",
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true
});

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'code_update' && data.sender !== roomData.username) {
        editor.setValue(data.content);
    } else if (data.type === 'room_state') {
        editor.setValue(data.content);
        editor.session.setMode(`ace/mode/${data.language}`);
    }
};

editor.session.on('change', function(delta) {
    socket.send(JSON.stringify({
        'type': 'code_update',
        'content': editor.getValue(),
        'sender': roomData.username
    }));
});

document.getElementById('save-btn').addEventListener('click', function() {
    fetch(roomData.saveUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': roomData.csrfToken
        },
        body: JSON.stringify({
            'content': editor.getValue()
        })
    }).then(response => {
        if (response.ok) {
            const toast = new bootstrap.Toast(document.getElementById('saveToast'));
            toast.show();
        } else {
            alert('Error saving content');
        }
    });
});