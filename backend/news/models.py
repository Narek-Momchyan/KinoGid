from django.db import models

class NewsPost(models.Model):
    title = models.CharField(max_length=500, verbose_name="Վերնագիր")
    content = models.TextField(verbose_name="Բովանդակություն")
    image_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Նկարի հղում")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ստեղծման ամսաթիվ")
    generated_by_ai = models.BooleanField(default=True, verbose_name="Գեներացված է AI-ի կողմից")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Նորություն"
        verbose_name_plural = "Նորություններ"

    def __str__(self):
        return self.title

class NewsComment(models.Model):
    news_post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='comments', verbose_name="Նորություն")
    author_name = models.CharField(max_length=255, verbose_name="Հեղինակի անուն")
    text = models.TextField(verbose_name="Մեկնաբանություն")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ստեղծման ամսաթիվ")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Մեկնաբանություն"
        verbose_name_plural = "Մեկնաբանություններ"

    def __str__(self):
        return f"{self.author_name} - {self.news_post.title}"
