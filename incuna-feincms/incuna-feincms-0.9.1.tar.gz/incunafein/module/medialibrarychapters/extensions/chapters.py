from incunafein.module.medialibrarychapters.models import MediaFileChapter, CHAPTER_TYPES
def register(cls, admin_cls):
    if admin_cls:
        from django.contrib import admin
        class MediaFileChaptersInline(admin.TabularInline):
            model = MediaFileChapter
            extra = 3
        admin_cls.inlines = list(admin_cls.inlines) + [MediaFileChaptersInline, ]

        def get_formsets(self, request, obj=None):
            for inline in self.inline_instances:
                # skip the MediaFileChapterInline for non video types
                if obj is None or type(inline)!=MediaFileChaptersInline or obj.type in CHAPTER_TYPES:
                    yield inline.get_formset(request, obj)
        admin_cls.get_formsets = get_formsets

