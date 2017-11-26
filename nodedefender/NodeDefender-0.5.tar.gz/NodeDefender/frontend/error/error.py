@app.errorhandler(403) # Trying to access without permission
@login_required
def page_not_allowed(e):
    return render_template('403.html'), 403

@app.errorhandler(404) # Trying to access page that does not exist.
@login_required
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500) # Internal Server Error
@login_required
def internal_server_error(e):
    return render_template('500.html'), 500
