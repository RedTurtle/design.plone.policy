from plone.namedfile.browser import DisplayFile as BaseView
from urllib.parse import quote


class DisplayFile(BaseView):
    """
    Custom view
    """

    def set_headers(self, file):
        """
        backport of https://github.com/RedTurtle/redturtle.volto/pull/113

        We need to add filename to the reponse because otherwise the browser
        use the field name as filename (last path element).

        content-disposition should be "inline" to allow to display the file in the browser
        without forcing download (with "attachment" the browser will download it).
        """
        super().set_headers(file=file)

        filename = getattr(file, "filename", "")
        if filename is not None:
            if not isinstance(filename, str):
                filename = str(filename, "utf-8", errors="ignore")
            filename = quote(filename.encode("utf8"))
            self.request.response.setHeader(
                "Content-Disposition", f"inline; filename*=UTF-8''{filename}"
            )
