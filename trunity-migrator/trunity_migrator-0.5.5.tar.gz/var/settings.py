#####################################################
#                  EXAMPLE OF CONF FILE
# Attention!! The following settings must be filled
# before running this script!
#####################################################

# set here your user name and password:
TRUNITY_2_LOGIN = "VicHunting2"
TRUNITY_2_PASSWORD = "jjj3030jja"

# PROD server creds:
TRUNITY_3_LOGIN = "hunting"
TRUNITY_3_PASSWORD = "good$education20017"

# STAGE server creds:
# TRUNITY_3_LOGIN = "zele@lucyu.com"
# TRUNITY_3_PASSWORD = "123qwe123"

# for final import:
# TRUNITY_3_LOGIN = "icbteam"
# TRUNITY_3_PASSWORD = "exam1234"

# the name of Trunity book you need to import:
# TRUNITY_2_BOOK_NAME = "Integrating Concepts in Biology"
# TRUNITY_2_BOOK_NAME = "ICB Sample Chapters for Debugging"
# TRUNITY_2_BOOK_NAME = "Science Fusion - Module C - Demo"

# TRUNITY_2_BOOK_NAME = "Holt McDougal Chemistry - Additional Resources"  # for Question Pools
# TRUNITY_2_BOOK_NAME = "test-questionnaire-migration-1"  # for Question Pools
# TRUNITY_2_BOOK_NAME = "Holt McDougal Chemistry - Additional Resources - Viktor"  # short version of HMH Chemistry
# TRUNITY_2_BOOK_NAME = "Life on this Rock: Biology - Test Sample Chapters"  # short version for self-on-learning
# TRUNITY_2_BOOK_NAME = "Multiple Answer - QP Test"
TRUNITY_2_BOOK_NAME = "Import Testing - Article Types"

# TRUNITY_3_BOOK_NAME = "HMH Chemistry Questionnaires - v1"
# TRUNITY_3_BOOK_NAME = "Questionnaire Temp 10"
# TRUNITY_3_BOOK_NAME = "HMH Chemistry (short version) v2"
# TRUNITY_3_BOOK_NAME = "Life on this Rock: Biology (short version) - v7"
# TRUNITY_3_BOOK_NAME = "Multiple Answer - QP Test"
TRUNITY_3_BOOK_NAME = "Import Testing - Article Types - v3"

# this will be added to all 'src' url
STATIC_URL = 'http://www.trunity.net'

# All of these content types will be saved.
# You may comment out what you don't need:
CONTENT_TYPES = [  # TODO: make global settings object
    "article",
    "questionpool",
    # "exam"
    # "news",
    # "video",
    # "podcast",
    # "gallery",
    "game",
    # "assignment",
    # "whitepaper",
    # "casestudy",
    # "presentation",
    # "lecture",
    # "exercise",
    # "teachingunit",
]


###############################################################################
#                           FIXERS SETTINGS
###############################################################################
FIXERS_ALLOWED = [
    'fix_img_src',
    # 'fix_table_width',
    # 'fix_science_fusion_style',
]


FIX_IMG_SRC = {
    "base_url": "http://www.trunity.net",
}

FIX_TABLE_WIDTH = {
    "old_widths": ["766", "770"],
    "new_widths": ["100%", "100%"],
}

FIX_SCIENCE_FUSION_STYLE = {}


