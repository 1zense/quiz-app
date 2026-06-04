// Auto-dismiss messages after 4 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            msg.style.transition = 'all 0.3s ease';
            setTimeout(function() { msg.remove(); }, 300);
        }, 4000);
    });
});
