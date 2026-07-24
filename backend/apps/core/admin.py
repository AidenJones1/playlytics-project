from django.contrib.admin import AdminSite

class NFLAdminSite(AdminSite):
    site_header = "Playlytics Admin Portal"
    site_title = "Playlytics Admin Portal"
    index_title = "Welcome to the Playlytics Admin Portal!"

playlytics_admin_site = NFLAdminSite(name="playlytics_admin")