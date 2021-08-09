from django.db import models
from django.contrib.auth.models import Group
from django.db import IntegrityError


# from django.contrib.auth.models import Group
# found = 0
#     groupName = "Creators"
#     groupCreators = Group.objects.all()

#     for groupCreator in groupCreators:
#         print("GROUP", groupCreator)
#         if groupName == groupCreator:
#             found = 1
#             break

#     print("FOUND:", found)
#     if found == 0:
#         print('GROUP CREATORS IS NOT AVAILABLE.')
#         Group.objects.create(name=groupName)

#########################################
# SUPERUSER                             #
#########################################
#  username: i22hadri                   #
#  email: hadriizz.work@gmail.com       #
#  password: admincomeldandisayangi123  #
#########################################


class Plan(models.Model):
    planName = models.CharField(
        max_length=100, blank=True, null=True)
    planPrice = models.CharField(max_length=100, blank=True, null=True)
    planDescription = models.CharField(max_length=300, blank=True, null=True)
    planStatus = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Creator(models.Model):
    try:
        Group.objects.create(name="Creator")
    except IntegrityError as e:
        print('Creator already EXIST.')
    creatorUsername = models.CharField(max_length=200, blank=True, null=True)
    creatorName = models.CharField(max_length=200, blank=True, null=True)
    creatorAge = models.CharField(max_length=3, blank=True, null=True)
    creatorOccupation = models.CharField(max_length=200, blank=True, null=True)
    planName = models.ForeignKey(
        Plan, null=True, on_delete=models.SET_NULL)

    # def __str__(self):
    #     return self.creatorName
