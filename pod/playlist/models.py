from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from pod.main.models import get_nextautoincrement
from pod.video.models import Video
from pod.video.utils import sort_videos_list

import hashlib


class Playlist(models.Model):
    """Playlist model."""
    VISIBILITY_CHOICES = [
        ("public", _("Public")),
        ("protected", _("Protected")),
        ("private", _("Private"))
    ]
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=250,
        default=_("Playlist"),
        help_text=_("Please choose a name between 1 and 250 characters."),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        default="",
        help_text=_("Please choose a description. This description is empty by default."),
    )
    password = models.TextField(
        verbose_name=_("Password"),
        blank=True,
        default="",
        help_text=_("Please choose a password if this playlist is protected."),
    )
    visibility = models.CharField(
        verbose_name=_("Visibility"),
        max_length=9,
        choices=VISIBILITY_CHOICES,
        default="private",
        help_text=_(
            '''
            Please chosse an visibility among 'public', 'protected', 'private'.
            '''
        ),
    )
    autoplay = models.BooleanField(
        verbose_name=_("Autoplay"),
        default=True,
        help_text=_("Please choose if this playlist is an autoplay playlist or not."),
    )
    editable = models.BooleanField(
        verbose_name=_("Editable"),
        default=True,
        help_text=_("Please choose if this playlist is editable or not."),
    )
    slug = models.SlugField(
        _("slug"),
        unique=True,
        max_length=105,
        help_text=_(
            'Used to access this instance, the "slug" is a short'
            + " label containing only letters, numbers, underscore"
            + " or dash top."
        ),
        editable=False,
    )
    owner = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    additional_owners = models.ManyToManyField(
        User,
        blank=True,
        verbose_name=_("Additional owners"),
        related_name="owners_playlists",
        help_text=_("You can add additional owners to the playlist."),
    )
    date_created = models.DateTimeField(
        verbose_name=_("Date created"),
        default=timezone.now,
        editable=False,
        auto_created=True,
    )
    date_updated = models.DateTimeField(
        verbose_name=_("Date updated"),
        editable=False,
        auto_now=True,
    )

    class Meta:
        """Metadata for Playlist model."""

        ordering = ["name", "owner", "visibility", "date_updated"]
        get_latest_by = "date_updated"
        verbose_name = _("Playlist")
        verbose_name_plural = _("Playlists")

    def save(self, *args, **kwargs) -> None:
        newid = -1
        if not self.id:
            try:
                newid = get_nextautoincrement(Playlist)
            except Exception:
                try:
                    newid = Playlist.objects.latest("id").id
                    newid += 1
                except Exception:
                    newid = 1
        else:
            newid = self.id
        self.slug = f"{newid}-{slugify(self.name)}"
        self.password = hashlib.sha256(self.password.encode("utf-8")).hexdigest()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        if self.visibility == "protected" and not self.password:
            raise ValidationError("Password is required for a protected playlist.")

    def __str__(self) -> str:
        """Display a playlist as string."""
        return self.slug

    def get_number_video(self) -> int:
        """Get the video number."""
        from .utils import get_number_video_in_playlist
        return get_number_video_in_playlist(self)

    def get_first_video(self) -> Video:
        """Get the first video."""
        from .utils import get_video_list_for_playlist
        return sort_videos_list(get_video_list_for_playlist(self), "rank").first()


class PlaylistContent(models.Model):
    """PlaylistContent model."""

    playlist = models.ForeignKey(Playlist, verbose_name=_(
        "Playlist"), on_delete=models.CASCADE)
    video = models.ForeignKey(Video, verbose_name=_("Video"), on_delete=models.CASCADE)
    date_added = models.DateTimeField(
        verbose_name=_("Date added"), default=timezone.now, editable=False
    )
    rank = models.IntegerField(verbose_name=_("Rank"), editable=False, default=1)

    class Meta:
        """Metadata for PlaylistContent model."""

        constraints = [
            # A video cannot be twice in a playlist.
            models.UniqueConstraint(
                fields=["playlist", "video"], name="unique_playlist_video"
            ),
        ]

        ordering = ["playlist", "rank"]
        get_latest_by = "rank"
        verbose_name = _("Playlist content")
        verbose_name_plural = _("Playlist contents")

    def save(self, *args, **kwargs) -> None:
        try:
            last_rank = PlaylistContent.objects.filter(
                playlist=self.playlist).aggregate(Max("rank"))["rank__max"]
            self.rank = last_rank + 1 if last_rank is not None else 1
        except Exception:
            ...
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Display a playlist content as string."""
        return f"Playlist : {self.playlist} - Video : {self.video} - Rank : {self.rank}"
