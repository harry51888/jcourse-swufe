from django.db import models
from django.utils import timezone

from jcourse_api.models import Department, Semester


class Category(models.Model):
    class Meta:
        verbose_name = '课程类别'
        ordering = ['name']
        verbose_name_plural = verbose_name

    name = models.CharField(verbose_name='名称', max_length=64, unique=True)

    def __str__(self):
        return self.name


class FormerCode(models.Model):
    class Meta:
        verbose_name = '曾用课号'
        verbose_name_plural = verbose_name
        ordering = ['old_code']
        constraints = [models.UniqueConstraint(fields=['old_code', 'new_code'], name='unique_record')]

    old_code = models.CharField(verbose_name='旧课号', max_length=32, unique=True, db_index=True)
    new_code = models.CharField(verbose_name='新课号', max_length=32, db_index=True)

    def __str__(self):
        return self.old_code


class Teacher(models.Model):
    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['tid', 'name'], name='unique_teacher')]

    tid = models.CharField(verbose_name='工号', max_length=32, null=True, blank=True, unique=True)
    name = models.CharField(verbose_name='姓名', max_length=255, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, verbose_name='单位', null=True, blank=True)
    title = models.CharField(verbose_name='职称', max_length=64, null=True, blank=True)
    pinyin = models.CharField(verbose_name='拼音', max_length=64, null=True, blank=True, db_index=True)
    abbr_pinyin = models.CharField(verbose_name='拼音缩写', max_length=64, null=True, blank=True, db_index=True)
    # 仅用于后台维护，不对外显示
    last_semester = models.ForeignKey(Semester, verbose_name='最后更新学期', null=True, blank=True,
                                      on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Course(models.Model):
    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        ordering = ['code']
        constraints = [models.UniqueConstraint(fields=['code', 'main_teacher'], name='unique_course')]

    code = models.CharField(verbose_name='课号', max_length=32, db_index=True)
    name = models.CharField(verbose_name='名称', max_length=255, db_index=True)
    categories = models.ManyToManyField(Category, verbose_name='类别', db_index=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, verbose_name='开课单位',
                                   null=True, blank=True, db_index=True)
    credit = models.FloatField(verbose_name='学分', default=0)
    main_teacher = models.ForeignKey(Teacher, verbose_name='主讲教师', on_delete=models.CASCADE, db_index=True)
    teacher_group = models.ManyToManyField(Teacher, verbose_name='教师组成', related_name='teacher_course')
    moderator_remark = models.TextField(verbose_name='管理员批注', null=True, blank=True, max_length=817)
    review_count = models.IntegerField(verbose_name='点评数', null=True, blank=True, default=0, db_index=True)
    review_avg = models.FloatField(verbose_name='平均评分', null=True, blank=True, default=0, db_index=True)
    # 仅用于后台维护，不对外显示
    last_semester = models.ForeignKey(Semester, verbose_name='最后更新学期', null=True, blank=True,
                                      on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.code} {self.name}（{self.main_teacher}）"

    def category_names(self):
        return ','.join(self.categories.all().values_list('name', flat=True))

    category_names.short_description = '类别'


class TeacherEvaluation(models.Model):
    """教师评价模型"""
    class Meta:
        verbose_name = '教师评价'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['teacher', 'source_data'], name='unique_teacher_evaluation')
        ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        verbose_name='教师',
        db_index=True,
        related_name='evaluations'
    )
    evaluation_content = models.TextField(
        verbose_name='评价内容',
        help_text='学生对教师的评价内容'
    )
    data_sources = models.CharField(
        verbose_name='数据来源',
        max_length=100,
        help_text='数据来源标识，如data-1,data-2'
    )
    evaluation_count = models.IntegerField(
        verbose_name='评价条数',
        default=1,
        help_text='该教师的评价条数'
    )
    source_data = models.CharField(
        verbose_name='原始数据标识',
        max_length=255,
        help_text='用于去重的原始数据标识',
        db_index=True
    )
    created_at = models.DateTimeField(
        verbose_name='创建时间',
        default=timezone.now,
        db_index=True
    )
    updated_at = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True
    )

    def __str__(self):
        return f"{self.teacher.name} - {self.evaluation_content[:50]}..."

    def get_evaluation_summary(self):
        """获取评价摘要"""
        if len(self.evaluation_content) > 100:
            return self.evaluation_content[:100] + "..."
        return self.evaluation_content

    get_evaluation_summary.short_description = '评价摘要'
