from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用户信息
    """
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default="avatars/default.png")
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    status=models.IntegerField(default=1)#1未申请，2申请待审核，3审核通过，4审核未通过
    def __str__(self):
        return self.username


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    def __str__(self):
        return self.title


class Post(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    content = models.TextField()

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    tags = models.ManyToManyField(
        to="Tag",
        through='Post2Tag',
        through_fields=('post', 'tag'),
    )

    def __str__(self):
        return self.title


class Post2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    post = models.ForeignKey(verbose_name='文章', to="Post", to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid', on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('post', 'tag'),
        ]

    def __str__(self):
        v = self.post.title + "---" + self.tag.title
        return v


class PostUpDown(models.Model):
    """
    点赞表
    """

    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE)
    post = models.ForeignKey("Post", null=True, on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('post', 'user'),
        ]


class Comment(models.Model):
    """

    评论表

    """
    nid = models.AutoField(primary_key=True)
    post = models.ForeignKey(verbose_name='评论文章', to='Post', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

# class mien(models.Model):
#     nid = models.AutoField(primary_key=True)
#     create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
#     pic = models.FileField(upload_to='mienpics/', default="mienpics/default.png")
#     user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    
#     def __str__(self):
#         return self.nid

class following(models.Model):
    nid = models.AutoField(primary_key=True)
    club = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE,related_name="club")
    fan = models.ForeignKey("UserInfo", null=True, on_delete=models.CASCADE,related_name="fan")

class Applications(models.Model):
    """

    申请表

    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name='申请人', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    content = models.CharField(verbose_name='申请理由', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    
    def __str__(self):
        return self.content
