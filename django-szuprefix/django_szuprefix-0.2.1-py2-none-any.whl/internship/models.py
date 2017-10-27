#!/usr/bin/env python   
# -*- coding:utf-8 -*-   
# Author: denishuang
import logging
import datetime
from . import choices
from django.contrib.auth.models import User
from django.db import models

from django_szuprefix.school.models import School, Teacher, Student, Session
from django_szuprefix.utils import modelutils
from django.contrib.contenttypes.fields import GenericRelation

log = logging.getLogger("django")


class InstructorCounsellorMixin(object):
    def __unicode__(self):
        return self.name

    def trainees_count(self):
        return self.trainees.count()

    trainees_count.short_description = u"学生数"

    def trainee_class_names(self):
        return ",".join([c or u'未知' for c in self.trainee_class_list()])

    trainee_class_names.short_description = u"所有班级"

    def trainee_college_names(self):
        return ",".join([c or u'未知' for c in self.trainee_colleges_list()])

    trainee_college_names.short_description = u"所有院系"

    def traineeclass_list(self, college=None):
        trainees = self.trainees
        if college and not college.startswith(u"全部"):
            trainees = trainees.filter(college=college)
        return modelutils.group_by(trainees, "clazz")

    def trainee_majors_list(self, college=None):
        trainees = self.trainees
        if college and not college.startswith(u"全部"):
            trainees = trainees.filter(college=college)
        return modelutils.group_by(trainees, "major")

    def trainee_colleges_list(self, trainee_type=None):
        return modelutils.group_by(self.get_trainees(trainee_type), "college")

    def save(self, **kwargs):
        if not self.name:
            self.name = self.teacher.name
        if not self.school:
            self.school = self.teacher.school
        return super(InstructorCounsellorMixin, self).save(**kwargs)


class Counsellor(InstructorCounsellorMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"指导老师"
        permissions = ()
        ordering = ("school", "name")

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_counsellors",
                               on_delete=models.PROTECT)
    teacher = models.OneToOneField(Teacher, verbose_name=Teacher._meta.verbose_name, null=True,
                                   related_name="as_internship_counsellor")
    name = models.CharField(u"姓名", max_length=32, db_index=True, null=True, blank=True)
    department = models.CharField(u"部门", max_length=64, null=True, blank=True)
    is_active = models.BooleanField(u"在职", blank=True, default=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    modify_time = models.DateTimeField(u"修改时间", auto_now=True)


class Instructor(InstructorCounsellorMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"辅导员"
        permissions = ()
        ordering = ("school", "name")

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_instructors",
                               on_delete=models.PROTECT)
    teacher = models.OneToOneField(Teacher, verbose_name=Teacher._meta.verbose_name, null=True,
                                   related_name="as_internship_instructor")
    name = models.CharField(u"姓名", max_length=32, db_index=True, null=True, blank=True)
    department = models.CharField(u"部门", max_length=64, null=True, blank=True)
    is_active = models.BooleanField(u"在职", blank=True, default=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    modify_time = models.DateTimeField(u"修改时间", auto_now=True)


class Trainee(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"实习生"
        # ordering = (,)

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_trainees",
                               on_delete=models.PROTECT)
    student = models.OneToOneField(Student, verbose_name=Student._meta.verbose_name, null=True,
                                related_name="as_internship_trainee",
                                on_delete=models.PROTECT)
    instructor = models.ForeignKey(Instructor, verbose_name=Instructor._meta.verbose_name, related_name="trainees",
                                   null=True,
                                   blank=True, on_delete=models.PROTECT)
    counsellor = models.ForeignKey(Counsellor, verbose_name=Counsellor._meta.verbose_name, related_name="trainees",
                                   null=True,
                                   blank=True, on_delete=models.PROTECT)
    name = models.CharField(u"姓名", max_length=64, null=True, blank=True)
    status = models.PositiveSmallIntegerField(u"实习状态",  default=choices.STATUS_WEISHIXI,
                                              choices=choices.CHOICES_STATUS, db_index=True)
    status_update_time = models.DateTimeField(u"实习状态修改时间", null=True, blank=True, default=None)
    last_institution = models.ForeignKey("Institution", verbose_name=u"最近工作单位", null=True, blank=True, related_name='trainees')
    current_institution = models.ForeignKey("Institution", verbose_name=u"当前工作单位", null=True, blank=True, related_name='current_trainees')
    last_signin_time = models.DateTimeField(verbose_name=u"最近签到时间", null=True, blank=True)
    last_feedback_time = models.DateTimeField(verbose_name=u"最近反馈时间", null=True, blank=True)
    last_recommend_time = models.DateTimeField(u"最近推荐校企职位时间", null=True, blank=True)
    last_browse_theme_time = models.DateTimeField(u"最近浏览帖子时间", blank=True, null=True, default=None)
    last_score_time = models.DateTimeField(u"最近评分时间", blank=True, null=True, default=None)
    score = models.PositiveSmallIntegerField(u"评分", blank=True, default=0)
    comment = models.TextField(u"备注", null=True, blank=True)
    ethnic_code = models.PositiveSmallIntegerField(u"民族代码", null=True, blank=True)
    admission_ticket = models.CharField(u"准考证", max_length=128, null=True, blank=True)
    leave_party_status = models.CharField(u"离校情况", max_length=128, null=True, blank=True)
    payment_status = models.CharField(u"缴费情况", max_length=128, null=True, blank=True)
    insurance_status = models.CharField(u"保险情况", max_length=128, null=True, blank=True)
    internship_report = models.CharField(u"实习报告", max_length=128, null=True, blank=True)
    internship_begin = models.DateField(u"实习期开始", blank=True, null=True)
    internship_end = models.DateField(u"实习期结束", blank=True, null=True)
    is_working = models.BooleanField(u"工作中", default=False)
    is_active = models.BooleanField(u"有效", default=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    modify_time = models.DateTimeField(u"修改时间", auto_now=True)

    def not_working_days(self):
        if not self.is_working and self.status_update_time:
            return datetime.date.today() - self.status_update_time
        return 0

    def __unicode__(self):
        return self.name

    def as_user(self):
        return self.student.as_user()

    def save(self, **kwargs):
        if not self.name:
            self.name = self.student.name
        self.school = self.student.school
        self.is_working = self.status in choices.WORKING_STATUS_LIST
        return super(Student, self).save(**kwargs)


class Institution(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"单位"
        ordering = ('-starting_date', '-id')

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_institutions",
                              on_delete=models.PROTECT)
    trainee = models.ForeignKey(Trainee, verbose_name=Trainee._meta.verbose_name, related_name="institutions",
                                on_delete=models.PROTECT)
    internship_type = models.PositiveSmallIntegerField(u"实习种类", default=1, null=True,
                                                       choices=choices.CHOICES_TYPE, blank=True)
    name = models.CharField(u"单位名称", max_length=128, null=True)
    oibc = models.CharField(u"组织机构代码", max_length=128, null=True, blank=True)
    city = models.CharField(u"单位地址", max_length=255, null=True)
    place = models.CharField(u"单位详细地址", max_length=255, null=True, blank=True)
    starting_date = models.DateField(u"上岗时间", null=True)
    finish_date = models.DateField(u"结束时间", null=True, blank=True)
    position = models.CharField(u"工作岗位", max_length=128, null=True, blank=True)
    salary = models.PositiveIntegerField(u"月薪", null=True)
    property = models.PositiveSmallIntegerField(u"单位性质", null=True, blank=True, choices=(
        (None, u"请选择"), (1, u"民营企业"), (2, u"国营企业"), (3, u"合资"), (4, u"其他"),))
    contacts = models.CharField(u"单位联系人", max_length=128, null=True)
    contact_number = models.CharField(u"单位联系电话", max_length=128, null=True)
    contact_email = models.CharField(u"单位联系邮箱", max_length=128, null=True, blank=True)
    party_recommend = models.PositiveSmallIntegerField(u"学校推荐种类", choices=choices.CHOICES_SCHOOL_RECOMMEND, null=True,
                                                       blank=True)
    is_party_recommend = models.NullBooleanField(u"是否学校推荐", choices=((None, u"请选择"), (True, u"是"), (False, u"否")),
                                                 default=None)
    comment = models.TextField(u"备注", null=True, blank=True)
    match_status = models.PositiveSmallIntegerField(u"专业对口", default=0, null=True, blank=True,
                                                    choices=choices.CHOICES_MATCH,
                                                    db_index=True)
    status = models.PositiveSmallIntegerField(u"实习状态", null=True, blank=False,
                                              choices=choices.CHOICES_STATUS,
                                              db_index=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

    # 额外字段
    graduate_goes = models.PositiveSmallIntegerField(u"毕业去向", null=True, blank=True,
                                                     choices=choices.CHOICES_GRADUATE_GOES,
                                                     db_index=True)
    institution_type = models.CharField(u"单位类型", max_length=8, null=True, blank=True,
                                        choices=choices.INSTITUTION_TYPE_CHOICES,
                                        db_index=True)
    institution_industry = models.CharField(u"单位所属行业", max_length=8, null=True, blank=True,
                                            choices=choices.INSTITUTION_INDUSTRY_CHOICES,
                                            db_index=True)
    behavior_intention = models.PositiveSmallIntegerField(u"使用意图", null=True, blank=True,
                                                          choices=choices.CHOICES_BEHAVIOR_INTENTION,
                                                          db_index=True)
    job_type = models.CharField(u"职业类型", max_length=8, null=True, blank=True, choices=choices.JOB_TYPE_CHOICES,
                                db_index=True)
    # contract_time = （上岗时间？）
    is_employed_hard = models.BooleanField(u"是否就业困难", blank=True, default=False,
                                           choices=( (True, u"是"), (False, u"否")))
    dispatch_nature = models.PositiveSmallIntegerField(u"派遣性质", null=True, blank=True,
                                                       choices=choices.CHOICES_DISPATCH_NATURE,
                                                       db_index=True)
    difficult_student_type = models.CharField(u"困难生类别", max_length=255, null=True, blank=True)

    #  difficult_student_type = models.PositiveSmallIntegerField(u"困难生类别",  null=True, blank=True, choices=GOVERNING_BODY_CHOICES,
    #                                           db_index=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.school = self.student.school
        it = self.internship_type
        if it in [choices.TYPE_WANGDIAN, choices.TYPE_JIAJIAO, choices.TYPE_SHENGXUE, choices.TYPE_CANJUN]:
            self.is_party_recommend = False
        if not self.position:
            self.position = choices.DEFAULTS_POSITION.get(it, self.get_internship_type_display())
        if not self.graduate_goes:
            self.graduate_goes = choices.DEFAULTS_GRADUATE_GOES.get(it, choices.QITAQINGKUANG)
        if not self.institution_type:
            self.institution_type = choices.DEFAULTS_INSTITUTION_TYPE.get(it, "")
        if not self.institution_industry:
            self.institution_industry = choices.DEFAULTS_INSTITUTION_INDUSTRY.get(it, "")
        if not self.behavior_intention:
            self.behavior_intention = choices.DEFAULTS_BEHAVIOR_INTENTION.get(it, choices.QITA)
        return super(Institution, self).save(**kwargs)




class Feedback(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"反馈"
        ordering = ('-create_time',)

    school = models.ForeignKey(School,verbose_name=School._meta.verbose_name,related_name="internship_feedbacks",on_delete=models.PROTECT)
    student = models.ForeignKey(Student, verbose_name=Student._meta.verbose_name, related_name="feedbacks",on_delete=models.PROTECT)
    institution = models.ForeignKey(Institution, verbose_name=u"单位", null=True, blank=True,on_delete=models.PROTECT)
    content = models.TextField(u"反馈", null=True)
    status = models.PositiveSmallIntegerField(u"实习状态", null=True, blank=True, choices=choices.CHOICES_STATUS, db_index=True)
    verify_status = models.PositiveSmallIntegerField(u"审核状态", default=0, null=True, blank=True, choices=choices.VERIFY_CHOICES,
                                                     db_index=True)
    teacher_remark = models.TextField(u"辅导员反馈", null=True, blank=True)
    teacher_score = models.PositiveIntegerField(u"辅导员打分", null=True, blank=True)
    create_time = models.DateTimeField(u"创建时间", db_index=True)
    images = GenericRelation("common.Image")

    def __unicode__(self):
        return u"%s %s feedback @%s" % (self.create_time.isoformat(),self.student,self.place)

    def save(self, **kwargs):
        self.school = self.student.school
        if not self.institution:
            self.institution = self.student.current_institution
        if not self.status:
            self.status = self.student.status
        return super(Feedback, self).save(**kwargs)

#
# class WishNew(models.Model):
#     class Meta:
#         verbose_name_plural = verbose_name = u"心愿单"
#         ordering = ('-create_time',)
#
#     SALARY_CHOICES = choices.SALARY_CHOICES
#
#     school = models.ForeignKey(School,verbose_name=u"公司",related_name="internship_wishs",on_delete=models.PROTECT)
#     student = models.OneToOneField(Student, verbose_name=u"实习生", related_name="wishnew",on_delete=models.PROTECT)
#     funtype = models.CharField(u"职能", max_length=128, null=True, blank=True)
#     indtype = models.CharField(u"行业", max_length=128, null=True, blank=True)
#     salary = models.CharField(u"薪水", max_length=8, null=True, blank=True, choices=choices.SALARY_CHOICES)
#     jobarea = models.CharField(u"地区", max_length=128, null=True, blank=True)
#     type = models.CharField(u"类型", max_length=8, null=True, blank=True,
#                             choices=((None, u"不限"), ("01", u"全职"), ("02", u"兼职"),))
#     create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
#     update_time = models.DateTimeField(u"修改时间", auto_now=True)
#
#     def save(self, **kwargs):
#         self.school = self.student.school
#         return super(WishNew, self).save(**kwargs)
#

# class Job(models.Model):
#     class Meta:
#         verbose_name_plural = verbose_name = u"工作"
#         unique_together = ("jobname", "coname", "city")
#         ordering = ('-create_time',)
#         permissions = (("manage_job", u"管理职位"),)
#
#     school = models.ForeignKey(School,verbose_name=u"公司",related_name="internship_jobs",on_delete=models.PROTECT)
#     teacher = models.ForeignKey(Teacher, verbose_name=u"教师", related_name="jobs", null=True)
#     worker = models.ForeignKey(Worker,verbose_name=u"员工", related_name="internship_jobs",on_delete=models.PROTECT)
#     coname = models.CharField(u"单位名称", max_length=128, default=None)
#     jobname = models.CharField(u"工作岗位", max_length=64, default=None)
#     property = models.PositiveSmallIntegerField(u"单位性质", choices=(
#         (None, u"请选择"), (1, u"民营企业"), (2, u"国营企业"), (3, u"合资"), (4, u"其他"),), default=None)
#     status = models.PositiveSmallIntegerField(u"工作类型", choices=((None, u"请选择"), (1, u"全职"), (2, u"兼职"),), default=None)
#     salary = models.PositiveSmallIntegerField(u"月薪", choices=((None, u"请选择"), (1, u"2000元以下"),
#                                                                 (2, u"2001~4000元/月"), (3, u"4001~6000元/月"), (4, u"6001~8000元/月"), (5, u"面议")), default=None)
#     jobnum = models.IntegerField(u"招聘人数", default=None)
#     city = models.CharField(u"工作城市", max_length=128, default=None)
#     place = models.CharField(u"单位详细地址", max_length=255, default=None)
#     responsibilities = models.TextField(u"岗位职责", default=None)
#     requirements = models.TextField(u"任职要求", default=None)
#     is_cooperation = models.PositiveSmallIntegerField(u"校企合作", choices=((None, u"请选择"), (1, u"是"), (2, u"不是"),), default=None)
#     introduce = models.TextField(u"公司简介", default=None)
#     contacts = models.CharField(u"单位联系人", max_length=128, default=None)
#     contact_number = models.CharField(u"单位联系电话", max_length=128, default=None)
#     email = models.CharField(u"单位邮箱", max_length=128, blank=True, null=True, default=None)
#     is_share = models.BooleanField(u"是否共享", choices=((True, u"共享"), (False, u"不共享")), default=True)
#     start_time = models.DateField(u"开始日期")
#     end_time = models.DateField(u"截止日期")
#     priority = models.IntegerField(u"优先级", default=0)
#     create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
#     update_time = models.DateTimeField(u"修改时间", auto_now=True)
#     remark = models.TextField(u"备注", null=True, blank=True)
#
#     def stat(self):
#         stat = datetime.date.today() <= self.end_time
#         return u"有效" if stat else u"失效"
#
#     def display_jobnum(self):
#         return self.jobnum == -1 and u"若干" or self.jobnum
#
#     def job_info(self):
#         return "%s,%s,%s,%s" % (self.coname, self.jobname, self.contacts, self.contact_number)
#
#     def recommend_sum(self):
#         return self.recommend_job.count()
#
#     def __unicode__(self):
#         return self.coname
#
#     def save(self, **kwargs):
#         self.school = self.worker.school
#         # 临时设置优先级
#         if self.school_id == 3:
#             self.priority = 100
#         return super(Job, self).save(**kwargs)
#
#
# class RecommendJob(models.Model):
#     class Meta:
#         verbose_name_plural = verbose_name = u"推荐工作"
#         ordering = ('-create_time',)
#
#     school = models.ForeignKey(School,verbose_name=u"公司",related_name="internship_recommend_jobs",on_delete=models.PROTECT)
#     student = models.ForeignKey(Student, verbose_name=u"学生", related_name="recommend_jobs")
#     job = models.ForeignKey(Job, verbose_name=u"工作", related_name="recommend_job")
#     create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
#
#     def save(self, **kwargs):
#         self.school = self.student.school
#         return super(RecommendJob, self).save(**kwargs)
#
#
# class Theme(models.Model):
#     class Meta:
#         verbose_name_plural = verbose_name = u"帖子"
#         ordering = ('-top', '-create_time',)
#
#     school = models.ForeignKey(School,verbose_name=u"公司",related_name="internship_themes",on_delete=models.PROTECT)
#     teacher = models.ForeignKey(Teacher, verbose_name=u"教师", related_name="themes")
#     title = models.CharField(u"标题", max_length=255  )
#     content = models.TextField(u"内容" )
#     top = models.BooleanField(u"置顶", choices=((None, u"请选择"), (True, u"是"), (False, u"否")), default=False)
#     comment_sum = models.PositiveIntegerField(u"评论数", default=0, null=True, blank=True)
#     create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
#     favorites =  GenericRelation(Favorite)
#     browses = GenericRelation(Browse)
#     praises = GenericRelation(Praise)
#     comments = GenericRelation(ThreadedComment,object_id_field="object_pk")
#     attachment = models.ManyToManyField(Resource,verbose_name=u"附件",related_name="themes",blank=True)
#     access_percent = models.FloatField(u"浏览率", default=0)
#
#     def un_access_count(self):
#         return self.teacher.counsel_students.cur_grade().count() - self.browses.count()
#
#     def __unicode__(self):
#         return self.title
#
#     def save(self, **kwargs):
#         self.school = self.teacher.school
#         return super(Theme, self).save(**kwargs)
#
#
# class ScoreHistory(models.Model):
#     class Meta:
#         verbose_name_plural = verbose_name = u"指导评分"
#         ordering = ('-create_time',)
#         unique_together = ('student','month')
#
#     school = models.ForeignKey(School,verbose_name=u"公司",related_name="internship_score_history",on_delete=models.PROTECT)
#     student = models.ForeignKey(Student, verbose_name=u"学生", related_name="scorehistory")
#     month = models.CharField(u"月份", max_length=10)
#     browse_count = models.PositiveIntegerField(u"本月看帖数", default=0, null=True, blank=True)
#     comment_count = models.PositiveIntegerField(u"本月回帖数", default=0, null=True, blank=True)
#     favorite_count = models.PositiveIntegerField(u"本月收藏数", default=0, null=True, blank=True)
#     signin_week_count = models.PositiveIntegerField(u"本月签到周数", default=0, null=True, blank=True)
#     score = models.PositiveSmallIntegerField(u"评分", default=0)
#     create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
#     update_time = models.DateTimeField(u"修改时间", auto_now=True)
#
#     def __unicode__(self):
#         return "%s,%s,%s" % (self.student,self.month,self.score)
#
#     def save(self, **kwargs):
#         self.school = self.student.school
#         return super(ScoreHistory, self).save(**kwargs)
