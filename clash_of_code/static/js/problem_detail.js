document.addEventListener('DOMContentLoaded', function() {
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.select();

        try {
            document.execCommand('copy');
            return true;
        } catch (err) {
            console.error('Не удалось скопировать текст', err);
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    }

    document.querySelectorAll('.copyable').forEach(pre => {
        pre.addEventListener('click', function() {
            const text = this.getAttribute('data-content');
            if (copyToClipboard(text)) {
                this.classList.add('copied');

                setTimeout(() => {
                    this.classList.remove('copied');
                }, 2000);
            }
        });
    });
});
