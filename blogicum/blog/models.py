from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        verbose_name='Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено', auto_now_add=True
    )

    class Meta:
        abstract = True


class Post(PublishedModel):
    title = models.CharField(verbose_name='Заголовок', max_length=256)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User, verbose_name='Автор публикации',
        on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        'Location', verbose_name='Местоположение',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    category = models.ForeignKey(
        'Category', verbose_name='Категория',
        on_delete=models.SET_NULL, null=True
    )
    image = models.ImageField(
        verbose_name='Изображение', upload_to='post_images/',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']


class Category(PublishedModel):
    title = models.CharField(verbose_name='Заголовок', max_length=256)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор', unique=True,
        help_text=('Идентификатор страницы для URL; разрешены '
                   'символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(verbose_name='Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    post = models.ForeignKey(
        Post,
        verbose_name='Публикация',
        related_name='comment',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий к публикации {self.post.title} от {self.author}.'
