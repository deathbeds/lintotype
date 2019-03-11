import typing as typ

class legacy:
    @classmethod
    def get_style_guide(
        cls, ignore: typ.List[typ.Text] = ..., select: typ.List[typ.Text] = ...
    ) -> StyleGuide: ...

class StyleGuide:
    def check_files(self, file_names: typ.List[typ.Text]) -> typ.Text: ...
