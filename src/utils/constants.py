class Action:
    MANAGE_MEMBERSHIP = "MANAGE_MEMBERSHIP"
    MANAGE_ATTENDANCE = "MANAGE_ATTENDANCE"
    VIEW_ACTIVE_MEMBERSHIP = "VIEW_ACTIVE_MEMBERSHIP"
    VIEW_ALL_MEMBERSHIPS = "VIEW_ALL_MEMBERSHIPS"
    CHECK_IN = "CHECK_IN"
    VIEW_ATTENDANCES = "VIEW_ATTENDANCES"
    CHANGE_SETTINGS = "CHANGE_SETTINGS"
    CHANGE_NAME = "CHANGE_NAME"
    CHANGE_PHONE = "CHANGE_PHONE"
    CHANGE_LOCALE = "CHANGE_LOCALE"
    ADD_MEMBERSHIP = "ADD_MEMBERSHIP"
    FREEZE_MEMBERSHIP = "FREEZE_MEMBERSHIP"
    UNFREEZE_MEMBERSHIP = "UNFREEZE_MEMBERSHIP"
    REGISTER = "REGISTER"
    CANCEL = "CANCEL"


class Modifier:
    BUTTON = "_button"
    TEXT = "_text"
    CALLBACK = "_callback"
    MEMBER = "member_"
    ADMIN = "admin_"
