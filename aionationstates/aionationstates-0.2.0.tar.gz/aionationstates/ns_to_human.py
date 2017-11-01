"""Contains impractical to obtain otherwise static data about NationStates.

I'd love to be able to request it from the API each time as opposed
to storing it, but NS makes it extremely difficult with the awkward
one-scale-at-a-time Census data interface and the buggy banner shard.

I claim no ownership over the NationStates content and really really
hope my usage of it can be considered Fair Use.
"""

from aionationstates.utils import banner_url


__all__ = ('ScaleInfo', 'Banner')

happening_filters = {
    'law', 'change', 'dispatch', 'rmb', 'embassy', 'eject', 'admin',
    'move', 'founding', 'cte', 'vote', 'resolution', 'member', 'endo',
}


dispatch_categories = {
    'Factbook': {
        'Overview',
        'History',
        'Geography',
        'Culture',
        'Politics',
        'Legislation',
        'Religion',
        'Military',
        'Economy',
        'International',
        'Trivia',
        'Miscellaneous',
    },
    'Bulletin': {
        'Policy',
        'News',
        'Opinion',
        'Campaign',
    },
    'Account': {
        'Military',
        'Trade',
        'Sport',
        'Drama',
        'Diplomacy',
        'Science',
        'Culture',
        'Other',
    },
    'Meta': {
        'Gameplay',
        'Reference',
    },
}


class ScaleInfo:
    """Static information about a World Census scale.

    Attributes
    ----------
    id : int
        The scale id, a number between 0 and 80.
    title : str
        The scale title. For example, `Civil Rights.`
    ranked : str
        A scale by which a nation or region is ranked, either in their
        region or the world. For example, `Most Extensive Civil Rights.`
    measurement : str
        The measurement scale. For example, `Martin Luther King, Jr. Units.`
    image : str
        An identifier NS uses for the Census tropy picture urls.
    nation_description : str
        Description for nations.
    region_description : str
        Description for regions.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


census_info = {
    0: ScaleInfo(
        id=0,
        title='Civil Rights',
        ranked='Most Extensive Civil Rights',
        measurement='Martin Luther King, Jr. Units',
        image='liberal',
        nation_description=('The citizens of nations ranked highly enjoy a '
                            'great amount of civil rights, or freedoms to '
                            'go about their personal business without '
                            'interference or regulation from government.'),
        region_description=('The citizens of regions ranked highly enjoy a '
                            'great amount of civil rights, or freedoms to '
                            'go about their personal business without '
                            'interference or regulation from government.'),
    ),
    1: ScaleInfo(
        id=1,
        title='Economy',
        ranked='Most Efficient Economies',
        measurement='Krugman-Greenspan Business Outlook Index',
        image='economy',
        nation_description=('Nations ranked highly are the most ruthlessly '
                            'efficient at translating raw resources, '
                            'including people, into economic output.'),
        region_description=('Regions ranked highly are the most ruthlessly '
                            'efficient at translating raw resources, '
                            'including people, into economic output.'),
    ),
    2: ScaleInfo(
        id=2,
        title='Political Freedom',
        ranked='Most Politically Free',
        measurement='Diebold Election Inking Scale',
        image='polifree',
        nation_description=('These nations allow citizens the greatest '
                            'amount of freedom to select their own '
                            'government.'),
        region_description=('These regions allow citizens the greatest '
                            'amount of freedom to select their own '
                            'government.'),
    ),
    3: ScaleInfo(
        id=3,
        title='Population',
        ranked='Largest Populations',
        measurement='Capita',
        image='population',
        nation_description=('The following nations have the greatest '
                            'number of citizens.'),
        region_description=('The following regions have the most citizens '
                            'per nation.'),
    ),
    4: ScaleInfo(
        id=4,
        title='Wealth Gaps',
        ranked='Greatest Rich-Poor Divides',
        measurement='Rich To Poor Income Ratio',
        image='wealthgaps',
        nation_description=('Nations ranked highly have large gaps between '
                            'the incomes of rich and poor citizens. '
                            'Nations low on the list have high levels of '
                            'income equality.'),
        region_description=('Regions ranked highly have large gaps between '
                            'the incomes of rich and poor citizens. '
                            'Regions low on the list have high levels of '
                            'income equality.'),
    ),
    5: ScaleInfo(
        id=5,
        title='Death Rate',
        ranked='Highest Unexpected Death Rate',
        measurement='Bus Surprisal Index',
        image='death',
        nation_description=('The World Census paid their respects at '
                            'cemeteries in order to determine how likely '
                            'citizens were to die each year from unnatural '
                            'causes, such as crime, preventable illness, '
                            'accident, and government encouragement.'),
        region_description=('The World Census paid their respects at '
                            'cemeteries in order to determine how likely '
                            'citizens were to die each year from unnatural '
                            'causes, such as crime, preventable illness, '
                            'accident, and government encouragement.'),
    ),
    6: ScaleInfo(
        id=6,
        title='Compassion',
        ranked='Most Compassionate Citizens',
        measurement='Kitten Softness Rating',
        image='compassionate',
        nation_description=('Exhaustive World Census tests involving '
                            'kittens revealed the following nations to be '
                            'the most compassionate.'),
        region_description=('Exhaustive World Census tests involving '
                            'kittens revealed the following regions to be '
                            'the most compassionate.'),
    ),
    7: ScaleInfo(
        id=7,
        title='Eco-Friendliness',
        ranked='Most Eco-Friendly Governments',
        measurement='Dolphin Recycling Awareness Index',
        image='eco-govt',
        nation_description=('The following governments spend the greatest '
                            'amounts on environmental issues. This may not '
                            'always be reflected in the quality of that '
                            "nation's environment."),
        region_description=('The following governments spend the greatest '
                            'amounts on environmental issues. This may not '
                            'always be reflected in the quality of that '
                            "region's environment."),
    ),
    8: ScaleInfo(
        id=8,
        title='Social Conservatism',
        ranked='Most Conservative',
        measurement='Bush-Santorum Dawning Terror Index',
        image='conservative',
        nation_description=('Citizens in nations ranked highly tend to '
                            'have greater restrictions placed on what they '
                            'may do in their personal lives, whether via '
                            'community values or government-imposed law.'),
        region_description=('Citizens in regions ranked highly tend to '
                            'have greater restrictions placed on what they '
                            'may do in their personal lives, whether via '
                            'community values or government-imposed law.'),
    ),
    9: ScaleInfo(
        id=9,
        title='Nudity',
        ranked='Nudest',
        measurement='Cheeks Per Square Mile',
        image='nude',
        nation_description=('After exhaustive surveys, the World Census '
                            'calculated which nations have the greatest '
                            'acreages of flesh on public display.'),
        region_description=('After exhaustive surveys, the World Census '
                            'calculated which regions have the greatest '
                            'acreages of flesh on public display.'),
    ),
    10: ScaleInfo(
        id=10,
        title='Industry: Automobile Manufacturing',
        ranked='Largest Automobile Manufacturing Sector',
        measurement='Henry Ford Productivity Index',
        image='auto',
        nation_description=('World Census analysts extensively tested '
                            'concept muscle cars in empty parking lots in '
                            'order to estimate which nations have the '
                            'largest auto industries.'),
        region_description=('World Census analysts extensively tested '
                            'concept muscle cars in empty parking lots in '
                            'order to estimate which regions have the '
                            'largest auto industries.'),
    ),
    11: ScaleInfo(
        id=11,
        title='Industry: Cheese Exports',
        ranked='Largest Cheese Export Sector',
        measurement='Mozzarella Productivity Index',
        image='cheese',
        nation_description=('Qualified World Census Cheese Masters nibbled '
                            'their way across the globe to determine which '
                            'nations have the most developed cheese '
                            'exports.'),
        region_description=('Qualified World Census Cheese Masters nibbled '
                            'their way across the globe to determine which '
                            'regions have the most developed cheese '
                            'exports.'),
    ),
    12: ScaleInfo(
        id=12,
        title='Industry: Basket Weaving',
        ranked='Largest Basket Weaving Sector',
        measurement='Hickory Productivity Index',
        image='basket',
        nation_description=('World Census agents infiltrated a variety of '
                            'out-of-the-way towns and festivals in order '
                            'to determine which nations have the most '
                            'developed Basket Weaving industries.'),
        region_description=('World Census agents infiltrated a variety of '
                            'out-of-the-way towns and festivals in order '
                            'to determine which regions have the most '
                            'developed Basket Weaving industries.'),
    ),
    13: ScaleInfo(
        id=13,
        title='Industry: Information Technology',
        ranked='Largest Information Technology Sector',
        measurement='Fann-Boi Productivity Index',
        image='tech',
        nation_description=('World Census staff compiled lists over Smart '
                            'Phone related traffic accidents to determine '
                            'which nations have the largest Information '
                            'Technology industries.'),
        region_description=('World Census staff compiled lists over Smart '
                            'Phone related traffic accidents to determine '
                            'which regions have the largest Information '
                            'Technology industries.'),
    ),
    14: ScaleInfo(
        id=14,
        title='Industry: Pizza Delivery',
        ranked='Largest Pizza Delivery Sector',
        measurement='Pepperoni Propulsion Productivity Index',
        image='pizza',
        nation_description=('World Census staff spent many nights '
                            'answering the front door in order to measure '
                            'which nations have the biggest Pizza Delivery '
                            'industries.'),
        region_description=('World Census staff spent many nights '
                            'answering the front door in order to measure '
                            'which regions have the biggest Pizza Delivery '
                            'industries.'),
    ),
    15: ScaleInfo(
        id=15,
        title='Industry: Trout Fishing',
        ranked='Largest Trout Fishing Sector',
        measurement='Nemo Depletion Efficiency Index',
        image='fish',
        nation_description=('The World Census conducted frenzied haggling '
                            'with fishmongers in order to determine which '
                            'nations have the largest fishing industries.'),
        region_description=('The World Census conducted frenzied haggling '
                            'with fishmongers in order to determine which '
                            'regions have the largest fishing industries.'),
    ),
    16: ScaleInfo(
        id=16,
        title='Industry: Arms Manufacturing',
        ranked='Largest Arms Manufacturing Sector',
        measurement='Charon Conveyancy Index',
        image='arms',
        nation_description=('World Census special forces intercepted '
                            'crates of smuggled weapons to determine which '
                            'nations have the largest arms industry.'),
        region_description=('World Census special forces intercepted '
                            'crates of smuggled weapons to determine which '
                            'regions have the largest arms industry.'),
    ),
    17: ScaleInfo(
        id=17,
        title='Sector: Agriculture',
        ranked='Largest Agricultural Sector',
        measurement='Mu-Bah-Daggs Productivity Index',
        image='agriculture',
        nation_description=('World Census bean-counters on horseback '
                            'guided herds of cattle to slaughter in order '
                            'to determine which nations have the largest '
                            'agricultural sectors.'),
        region_description=('World Census bean-counters on horseback '
                            'guided herds of cattle to slaughter in order '
                            'to determine which regions have the largest '
                            'agricultural sectors.'),
    ),
    18: ScaleInfo(
        id=18,
        title='Industry: Beverage Sales',
        ranked='Largest Soda Pop Sector',
        measurement='Addison-Fukk Productivity Rating',
        image='soda',
        nation_description=('The World Census recorded sales of fizzy '
                            'syrup water in order to determine which '
                            'nations have the largest beverage industries.'),
        region_description=('The World Census recorded sales of fizzy '
                            'syrup water in order to determine which '
                            'regions have the largest beverage industries.'),
    ),
    19: ScaleInfo(
        id=19,
        title='Industry: Timber Woodchipping',
        ranked='Largest Timber Woodchipping Industry',
        measurement='Tasmanian Pulp Environmental Export Index',
        image='timber',
        nation_description=('The World Census measured the rate of '
                            'desertification in order to calculate which '
                            'nations have the largest timber industry.'),
        region_description=('The World Census measured the rate of '
                            'desertification in order to calculate which '
                            'regions have the largest timber industry.'),
    ),
    20: ScaleInfo(
        id=20,
        title='Industry: Mining',
        ranked='Largest Mining Sector',
        measurement='Blue Sky Asbestos Index',
        image='mining',
        nation_description=('World Census experts measured the volume of '
                            'stuff removed from the ground to determine '
                            'which nations have the largest mining '
                            'industries.'),
        region_description=('World Census experts measured the volume of '
                            'stuff removed from the ground to determine '
                            'which regions have the largest mining '
                            'industries.'),
    ),
    21: ScaleInfo(
        id=21,
        title='Industry: Insurance',
        ranked='Largest Insurance Industry',
        measurement='Risk Expulsion Effectiveness Rating',
        image='insurance',
        nation_description=('The World Census posed as door-to-door '
                            'salespeople in order to establish which '
                            'nations have the most extensive Insurance '
                            'industries.'),
        region_description=('The World Census posed as door-to-door '
                            'salespeople in order to establish which '
                            'regions have the most extensive Insurance '
                            'industries.'),
    ),
    22: ScaleInfo(
        id=22,
        title='Industry: Furniture Restoration',
        ranked='Largest Furniture Restoration Industry',
        measurement='Spitz-Pollish Productivity Index',
        image='furniture',
        nation_description=('World Census analysts spend quiet weekends in '
                            'the countryside in order to determine which '
                            'nations have the largest Furniture '
                            'Restoration industries.'),
        region_description=('World Census analysts spend quiet weekends in '
                            'the countryside in order to determine which '
                            'regions have the largest Furniture '
                            'Restoration industries.'),
    ),
    23: ScaleInfo(
        id=23,
        title='Industry: Retail',
        ranked='Largest Retail Industry',
        measurement='Shrinkwrap Consignment Productivity Index',
        image='retail',
        nation_description=('The World Census estimated levels of employee '
                            'ennui to determine which nations have the '
                            'largest retail industries.'),
        region_description=('The World Census estimated levels of employee '
                            'ennui to determine which regions have the '
                            'largest retail industries.'),
    ),
    24: ScaleInfo(
        id=24,
        title='Industry: Book Publishing',
        ranked='Largest Publishing Industry',
        measurement='Bella Potter Productivity e-Index',
        image='publishing',
        nation_description=('The World Census tallied social media '
                            'complaints from students regarding overpriced '
                            'textbooks to determine which nations have the '
                            'largest book publishing industries.'),
        region_description=('The World Census tallied social media '
                            'complaints from students regarding overpriced '
                            'textbooks to determine which regions have the '
                            'largest book publishing industries.'),
    ),
    25: ScaleInfo(
        id=25,
        title='Industry: Gambling',
        ranked='Largest Gambling Industry',
        measurement='Kelly Criterion Productivity Index',
        image='gambling',
        nation_description=('The World Census tailed known underworld '
                            'figures in order to determine which nations '
                            'have the largest gambling industries.'),
        region_description=('The World Census tailed known underworld '
                            'figures in order to determine which regions '
                            'have the largest gambling industries.'),
    ),
    26: ScaleInfo(
        id=26,
        title='Sector: Manufacturing',
        ranked='Largest Manufacturing Sector',
        measurement='Gooback-Jerbs Productivity Index',
        image='manufacturing',
        nation_description=('World Census bean-counters tabulated data '
                            'from across several industries in order to '
                            'determine which nations have the largest '
                            'Manufacturing sectors.'),
        region_description=('World Census bean-counters tabulated data '
                            'from across several industries in order to '
                            'determine which regions have the largest '
                            'Manufacturing sectors.'),
    ),
    27: ScaleInfo(
        id=27,
        title='Government Size',
        ranked='Largest Governments',
        measurement='Bureaucratic Comprehensiveness Rating Scale Index',
        image='govt',
        nation_description=('World Census agents lined up at public '
                            'agencies around the world in order to study '
                            'the extent of government in nations, taking '
                            'into consideration economic output, social '
                            'and cultural significance, and raw size.'),
        region_description=('World Census agents lined up at public '
                            'agencies around the world in order to study '
                            'the extent of government in regions, taking '
                            'into consideration economic output, social '
                            'and cultural significance, and raw size.'),
    ),
    28: ScaleInfo(
        id=28,
        title='Welfare',
        ranked='Largest Welfare Programs',
        measurement='Safety Net Mesh Density Rating',
        image='welfare',
        nation_description=('Governments ranked highly spend the most on '
                            'social welfare programs. Nations ranked low '
                            'tend to have weak or non-existent government '
                            'welfare.'),
        region_description=('Governments ranked highly spend the most on '
                            'social welfare programs. Regions ranked low '
                            'tend to have weak or non-existent government '
                            'welfare.'),
    ),
    29: ScaleInfo(
        id=29,
        title='Public Healthcare',
        ranked='Most Extensive Public Healthcare',
        measurement='Theresa-Nightingale Rating',
        image='healthcare',
        nation_description=('World Census interns were infected with '
                            'obscure diseases in order to test which '
                            'nations had the most effective and '
                            'well-funded public healthcare facilities.'),
        region_description=('World Census interns were infected with '
                            'obscure diseases in order to test which '
                            'regions had the most effective and '
                            'well-funded public healthcare facilities.'),
    ),
    30: ScaleInfo(
        id=30,
        title='Law Enforcement',
        ranked='Most Advanced Law Enforcement',
        measurement='Orwell Orderliness Index',
        image='police',
        nation_description=('World Census interns were framed for minor '
                            'crimes in order to measure the response '
                            'times, effectiveness, and amount of firepower '
                            'deployed by the law enforcement agencies of '
                            'different nations.'),
        region_description=('World Census interns were framed for minor '
                            'crimes in order to measure the response '
                            'times, effectiveness, and amount of firepower '
                            'deployed by the law enforcement agencies of '
                            'different regions.'),
    ),
    31: ScaleInfo(
        id=31,
        title='Business Subsidization',
        ranked='Most Subsidized Industry',
        measurement='Gilded Widget Scale',
        image='business',
        nation_description=('Nations ranked highly spend the most on '
                            'developing and supporting industry, a '
                            "practice known as 'corporate welfare.'"),
        region_description=('Regions ranked highly spend the most on '
                            'developing and supporting industry, a '
                            "practice known as 'corporate welfare.'"),
    ),
    32: ScaleInfo(
        id=32,
        title='Religiousness',
        ranked='Most Devout',
        measurement='Prayers Per Hour',
        image='devout',
        nation_description=('World Census Inquisitors conducted rigorous '
                            'one-on-one interviews probing the depth of '
                            "citizens' beliefs in order to determine which "
                            'nations were the most devout.'),
        region_description=('World Census Inquisitors conducted rigorous '
                            'one-on-one interviews probing the depth of '
                            "citizens' beliefs in order to determine which "
                            'regions were the most devout.'),
    ),
    33: ScaleInfo(
        id=33,
        title='Income Equality',
        ranked='Most Income Equality',
        measurement='Marx-Engels Emancipation Scale',
        image='equality',
        nation_description=('World Census boffins calculated the '
                            'difference in incomes between the richest and '
                            'poorest citizens, where a score of 50 would '
                            'mean that poor incomes are 50% of rich '
                            'incomes.'),
        region_description=('World Census boffins calculated the '
                            'difference in incomes between the richest and '
                            'poorest citizens, where a score of 50 would '
                            'mean that poor incomes are 50% of rich '
                            'incomes.'),
    ),
    34: ScaleInfo(
        id=34,
        title='Niceness',
        ranked='Nicest Citizens',
        measurement='Average Smiles Per Day',
        image='nice',
        nation_description=('World Census sociology experts studied '
                            'citizens from various nations to determine '
                            'which seemed most friendly and concerned for '
                            'others.'),
        region_description=('World Census sociology experts studied '
                            'citizens from various regions to determine '
                            'which seemed most friendly and concerned for '
                            'others.'),
    ),
    35: ScaleInfo(
        id=35,
        title='Rudeness',
        ranked='Rudest Citizens',
        measurement='Insults Per Minute',
        image='rude',
        nation_description=('World Census experts telephoned citizens from '
                            'all nations at just before dinner time, in a '
                            'study to determine which populations were '
                            'most brash, rude, or brusque.'),
        region_description=('World Census experts telephoned citizens from '
                            'all regions at just before dinner time, in a '
                            'study to determine which populations were '
                            'most brash, rude, or brusque.'),
    ),
    36: ScaleInfo(
        id=36,
        title='Intelligence',
        ranked='Smartest Citizens',
        measurement='Quips Per Hour',
        image='smart',
        nation_description=('The World Census eavesdropped on '
                            'conversations in coffee shops, on campuses, '
                            'and around cinemas in order to determine '
                            'which nations have the most quick-witted, '
                            'insightful, and knowledgeable citizens.'),
        region_description=('The World Census eavesdropped on '
                            'conversations in coffee shops, on campuses, '
                            'and around cinemas in order to determine '
                            'which regions have the most quick-witted, '
                            'insightful, and knowledgeable citizens.'),
    ),
    37: ScaleInfo(
        id=37,
        title='Ignorance',
        ranked='Most Ignorant Citizens',
        measurement='Missed References Per Hour',
        image='stupid',
        nation_description=('The World Census studied which nations seemed '
                            'to have the greatest numbers of citizens that '
                            'fell into the categories "ignorant," '
                            '"oblivious," or "just plain dumb."'),
        region_description=('The World Census studied which regions seemed '
                            'to have the greatest numbers of citizens that '
                            'fell into the categories "ignorant," '
                            '"oblivious," or "just plain dumb."'),
    ),
    38: ScaleInfo(
        id=38,
        title='Political Apathy',
        ranked='Most Politically Apathetic Citizens',
        measurement='Whatever',
        image='apathetic',
        nation_description=('These results were determined by seeing how '
                            'many citizens of each nation answered a '
                            'recent World Census survey on the local '
                            'political situation by ticking the "Don\'t '
                            'Give a Damn" box.'),
        region_description=('These results were determined by seeing how '
                            'many citizens of each region answered a '
                            'recent World Census survey on the local '
                            'political situation by ticking the "Don\'t '
                            'Give a Damn" box.'),
    ),
    39: ScaleInfo(
        id=39,
        title='Health',
        ranked='Healthiest Citizens',
        measurement='Bananas Ingested Per Day',
        image='healthy',
        nation_description=('A measure of the general physical health of '
                            'citizens in each nation.'),
        region_description=('A measure of the general physical health of '
                            'citizens in each region.'),
    ),
    40: ScaleInfo(
        id=40,
        title='Cheerfulness',
        ranked='Most Cheerful Citizens',
        measurement='Percentage Of Water Glasses Perceived Half-Full',
        image='happy',
        nation_description=('The World Census shared cheeky grins with '
                            'citizens around the world in order to '
                            'determine which were the most relentlessly '
                            'cheerful.'),
        region_description=('The World Census shared cheeky grins with '
                            'citizens around the world in order to '
                            'determine which were the most relentlessly '
                            'cheerful.'),
    ),
    41: ScaleInfo(
        id=41,
        title='Weather',
        ranked='Best Weather',
        measurement='Meters Of Sunlight',
        image='weather',
        nation_description=('The following nations were determined to have '
                            'the best all-round weather.'),
        region_description=('The following regions were determined to have '
                            'the best all-round weather.'),
    ),
    42: ScaleInfo(
        id=42,
        title='Compliance',
        ranked='Lowest Crime Rates',
        measurement='Law-abiding Acts Per Hour',
        image='lowcrime',
        nation_description=('World Census agents attempted to lure '
                            'citizens into committing various crimes in '
                            'order to test the reluctance of citizens to '
                            'break the law.'),
        region_description=('World Census agents attempted to lure '
                            'citizens into committing various crimes in '
                            'order to test the reluctance of citizens to '
                            'break the law.'),
    ),
    43: ScaleInfo(
        id=43,
        title='Safety',
        ranked='Safest',
        measurement='Bubble-Rapp Safety Rating',
        image='safe',
        nation_description=('World Census agents tested the sharpness of '
                            "household objects, the softness of children's "
                            'play equipment, and the survival rate of '
                            'people taking late walks to determine how '
                            'safe each nation is to visit.'),
        region_description=('World Census agents tested the sharpness of '
                            "household objects, the softness of children's "
                            'play equipment, and the survival rate of '
                            'people taking late walks to determine how '
                            'safe each region is to visit.'),
    ),
    44: ScaleInfo(
        id=44,
        title='Lifespan',
        ranked='Longest Average Lifespans',
        measurement='Years',
        image='life',
        nation_description=('Nations ranked highly have lower rates of '
                            'preventable death, with their citizens '
                            'enjoying longer average lifespans.'),
        region_description=('Regions ranked highly have lower rates of '
                            'preventable death, with their citizens '
                            'enjoying longer average lifespans.'),
    ),
    45: ScaleInfo(
        id=45,
        title='Ideological Radicality',
        ranked='Most Extreme',
        measurement='Paul-Nader Subjective Decentrality Index',
        image='extreme',
        nation_description=('The World Census ranked nations on the basis '
                            'of how odd, extreme, or fundamentalist their '
                            'social, economic, and political systems are.'),
        region_description=('The World Census ranked regions on the basis '
                            'of how odd, extreme, or fundamentalist their '
                            'social, economic, and political systems are.'),
    ),
    46: ScaleInfo(
        id=46,
        title='Defense Forces',
        ranked='Most Advanced Defense Forces',
        measurement='Total War Preparedness Rating',
        image='defense',
        nation_description=('Nations ranked highly spend the most on '
                            'national defense, and are most secure against '
                            'foreign aggression.'),
        region_description=('Regions ranked highly spend the most on '
                            'regional defense, and are most secure against '
                            'foreign aggression.'),
    ),
    47: ScaleInfo(
        id=47,
        title='Pacifism',
        ranked='Most Pacifist',
        measurement='Cheeks Turned Per Day',
        image='peace',
        nation_description=('Nations ranked highly pursue diplomatic '
                            'solutions rather than military ones in the '
                            'international arena, have small or '
                            'nonexistent militaries, and peace-loving '
                            'citizens.'),
        region_description=('Regions ranked highly pursue diplomatic '
                            'solutions rather than military ones in the '
                            'international arena, have small or '
                            'nonexistent militaries, and peace-loving '
                            'citizens.'),
    ),
    48: ScaleInfo(
        id=48,
        title='Economic Freedom',
        ranked='Most Pro-Market',
        measurement='Rand Index',
        image='pro-market',
        nation_description=('This data was compiled by surveying a random '
                            'sample of businesses with the question, "Do '
                            'you believe the government is committed to '
                            'free market policies?"'),
        region_description=('This data was compiled by surveying a random '
                            'sample of businesses with the question, "Do '
                            'you believe the government is committed to '
                            'free market policies?"'),
    ),
    49: ScaleInfo(
        id=49,
        title='Taxation',
        ranked='Highest Average Tax Rates',
        measurement='Effective Tax Rate',
        image='hightax',
        nation_description=('Although some nations have a flat tax rate '
                            'for all citizens while others tax the rich '
                            'more heavily than the poor, the World Census '
                            "used averages to rank the world's most taxing "
                            'governments.'),
        region_description=('Although some regions have a flat tax rate '
                            'for all citizens while others tax the rich '
                            'more heavily than the poor, the World Census '
                            "used averages to rank the world's most taxing "
                            'governments.'),
    ),
    50: ScaleInfo(
        id=50,
        title='Freedom From Taxation',
        ranked='Lowest Overall Tax Burden',
        measurement='Hayek Index',
        image='lowtax',
        nation_description=('World Census financial experts assessed '
                            'nations across a range of direct and indirect '
                            'measures in order to determine which placed '
                            'the lowest tax burden on their citizens.'),
        region_description=('World Census financial experts assessed '
                            'regions across a range of direct and indirect '
                            'measures in order to determine which placed '
                            'the lowest tax burden on their citizens.'),
    ),
    51: ScaleInfo(
        id=51,
        title='Corruption',
        ranked='Most Corrupt Governments',
        measurement='Kickbacks Per Hour',
        image='corrupt',
        nation_description=('World Census officials visited a range of '
                            'government departments and recorded how '
                            'frequently bribes were required to complete '
                            'simple administrative requests.'),
        region_description=('World Census officials visited a range of '
                            'government departments and recorded how '
                            'frequently bribes were required to complete '
                            'simple administrative requests.'),
    ),
    52: ScaleInfo(
        id=52,
        title='Integrity',
        ranked='Least Corrupt Governments',
        measurement='Percentage Of Bribes Refused',
        image='leastcorrupt',
        nation_description=('World Census agents tempted government '
                            'officials with financial and other '
                            'inducements to bend the rules and recorded '
                            'how often their proposals were declined.'),
        region_description=('World Census agents tempted government '
                            'officials with financial and other '
                            'inducements to bend the rules and recorded '
                            'how often their proposals were declined.'),
    ),
    53: ScaleInfo(
        id=53,
        title='Authoritarianism',
        ranked='Most Authoritarian',
        measurement='Stalins',
        image='authoritarian',
        nation_description=('World Census staff loitered innocuously in '
                            'various public areas and recorded the length '
                            'of time that passed before they were '
                            'approached by dark-suited officials.'),
        region_description=('World Census staff loitered innocuously in '
                            'various public areas and recorded the length '
                            'of time that passed before they were '
                            'approached by dark-suited officials.'),
    ),
    54: ScaleInfo(
        id=54,
        title='Youth Rebelliousness',
        ranked='Most Rebellious Youth',
        measurement='Stark-Dean Displacement Index',
        image='rebelyouth',
        nation_description=('World Census observers counted the number of '
                            'times their car stereo was stolen from '
                            'outside fast food stores to determine which '
                            'nations have relatively high levels of '
                            'youth-related crime.'),
        region_description=('World Census observers counted the number of '
                            'times their car stereo was stolen from '
                            'outside fast food stores to determine which '
                            'regions have relatively high levels of '
                            'youth-related crime.'),
    ),
    55: ScaleInfo(
        id=55,
        title='Culture',
        ranked='Most Cultured',
        measurement='Snufflebottom-Wiggendum Pentatonic Scale',
        image='culture',
        nation_description=('After spending many tedious hours in coffee '
                            'shops and concert halls, World Census experts '
                            'have found the following nations to be the '
                            'most cultured.'),
        region_description=('After spending many tedious hours in coffee '
                            'shops and concert halls, World Census experts '
                            'have found the following regions to be the '
                            'most cultured.'),
    ),
    56: ScaleInfo(
        id=56,
        title='Employment',
        ranked='Highest Workforce Participation Rate',
        measurement='Workforce Participation Rate',
        image='employed',
        nation_description=('World Census experts studied the ratings of '
                            'daytime television chat shows to estimate the '
                            'percentage of citizens who are employed.'),
        region_description=('World Census experts studied the ratings of '
                            'daytime television chat shows to estimate the '
                            'percentage of citizens who are employed.'),
    ),
    57: ScaleInfo(
        id=57,
        title='Public Transport',
        ranked='Most Advanced Public Transport',
        measurement='Societal Mobility Rating',
        image='publictransport',
        nation_description=('World Census experts captured, tagged, and '
                            'released trains in order to identify which '
                            'nations have the most extensive, well-funded '
                            'public transportation systems.'),
        region_description=('World Census experts captured, tagged, and '
                            'released trains in order to identify which '
                            'regions have the most extensive, well-funded '
                            'public transportation systems.'),
    ),
    58: ScaleInfo(
        id=58,
        title='Tourism',
        ranked='Most Popular Tourist Destinations',
        measurement='Tourists Per Hour',
        image='tourism',
        nation_description=('World Census experts tracked millions of '
                            'international tourists in order to determine '
                            "the world's favourite nations to sight-see."),
        region_description=('World Census experts tracked millions of '
                            'international tourists in order to determine '
                            "the world's favourite regions to sight-see."),
    ),
    59: ScaleInfo(
        id=59,
        title='Weaponization',
        ranked='Most Armed',
        measurement='Weapons Per Person',
        image='armed',
        nation_description=('World Census experts took their lives into '
                            'their hands in order to ascertain the average '
                            'number of deadly weapons per citizen.'),
        region_description=('World Census experts took their lives into '
                            'their hands in order to ascertain the average '
                            'number of deadly weapons per citizen.'),
    ),
    60: ScaleInfo(
        id=60,
        title='Recreational Drug Use',
        ranked='Highest Drug Use',
        measurement='Pineapple Fondness Rating',
        image='drugs',
        nation_description=('World Census experts sampled many cakes of '
                            "dubious content to determine which nations' "
                            'citizens consume the most recreational drugs.'),
        region_description=('World Census experts sampled many cakes of '
                            "dubious content to determine which regions' "
                            'citizens consume the most recreational drugs.'),
    ),
    61: ScaleInfo(
        id=61,
        title='Obesity',
        ranked='Fattest Citizens',
        measurement='Obesity Rate',
        image='fat',
        nation_description=('World Census takers tracked the sale of '
                            'Cheetos and Twinkies to ascertain which '
                            'nations most enjoyed the "kind bud."'),
        region_description=('World Census takers tracked the sale of '
                            'Cheetos and Twinkies to ascertain which '
                            'regions most enjoyed the "kind bud."'),
    ),
    62: ScaleInfo(
        id=62,
        title='Secularism',
        ranked='Most Secular',
        measurement='Atheism Rate',
        image='godforsaken',
        nation_description=('World Census experts studied which citizens '
                            'seemed least concerned about eternal '
                            'damnation, spiritual awakeness, and chakra '
                            'wellbeing in order to determine the most '
                            'godforsaken nations.'),
        region_description=('World Census experts studied which citizens '
                            'seemed least concerned about eternal '
                            'damnation, spiritual awakeness, and chakra '
                            'wellbeing in order to determine the most '
                            'godforsaken regions.'),
    ),
    63: ScaleInfo(
        id=63,
        title='Environmental Beauty',
        ranked='Most Beautiful Environments',
        measurement='Pounds Of Wildlife Per Square Mile',
        image='environment',
        nation_description=('World Census researchers spent many arduous '
                            'weeks lying on beaches and trekking through '
                            'rainforests to compile a definitive list of '
                            'the most attractive and best cared for '
                            'environments.'),
        region_description=('World Census researchers spent many arduous '
                            'weeks lying on beaches and trekking through '
                            'rainforests to compile a definitive list of '
                            'the most attractive and best cared for '
                            'environments.'),
    ),
    64: ScaleInfo(
        id=64,
        title='Charmlessness',
        ranked='Most Avoided',
        measurement='Kardashian Reflex Score',
        image='avoided',
        nation_description=('Nations ranked highly are considered by many '
                            'to be the most inhospitable, charmless, and '
                            'ghastly places to spend a vacation, or, '
                            'indeed, any time at all.'),
        region_description=('Regions ranked highly are considered by many '
                            'to be the most inhospitable, charmless, and '
                            'ghastly places to spend a vacation, or, '
                            'indeed, any time at all.'),
    ),
    65: ScaleInfo(
        id=65,
        title='Influence',
        ranked='Most Influential',
        measurement='Soft Power Disbursement Rating',
        image='influence',
        nation_description=('World Census experts spent many evenings '
                            'loitering in the corridors of power in order '
                            'to determine which nations were the greatest '
                            'international diplomacy heavyweights.'),
        region_description=('World Census experts spent many evenings '
                            'loitering in the corridors of power in order '
                            'to determine which regions were the greatest '
                            'international diplomacy heavyweights.'),
    ),
    66: ScaleInfo(
        id=66,
        title='World Assembly Endorsements',
        ranked='Most World Assembly Endorsements',
        measurement='Valid Endorsements',
        image='endorsed',
        nation_description=('World Census staff pored through World '
                            'Assembly records to determine which nations '
                            'were the most endorsed by others in their '
                            'region.'),
        region_description=('World Census staff pored through World '
                            'Assembly records to determine the average '
                            'number of endorsements per nation in each '
                            'region.'),
    ),
    67: ScaleInfo(
        id=67,
        title='Averageness',
        ranked='Most Average',
        measurement='Average Standardized Normality Scale',
        image='average',
        nation_description=('World Census staff took time out to pay '
                            'tribute to those most overlooked of nations: '
                            'the determinedly average.'),
        region_description=('World Census staff took time out to pay '
                            'tribute to those most overlooked of regions: '
                            'the determinedly average.'),
    ),
    68: ScaleInfo(
        id=68,
        title='Human Development Index',
        ranked='Most Developed',
        measurement='Human Development Index',
        image='hdi',
        nation_description=('The World Census compiles a "Human '
                            'Development Index" by measuring citizens\' '
                            'average life expectancy, education, and '
                            'income.'),
        region_description=('The World Census compiles a "Human '
                            'Development Index" by measuring citizens\' '
                            'average life expectancy, education, and '
                            'income.'),
    ),
    69: ScaleInfo(
        id=69,
        title='Primitiveness',
        ranked='Most Primitive',
        measurement='Scary Big Number Scale',
        image='primitive',
        nation_description=('Nations were ranked by World Census officials '
                            'based on the number of natural phenomena '
                            'attributed to the unknowable will of '
                            'animal-based spirit gods.'),
        region_description=('Regions were ranked by World Census officials '
                            'based on the number of natural phenomena '
                            'attributed to the unknowable will of '
                            'animal-based spirit gods.'),
    ),
    70: ScaleInfo(
        id=70,
        title='Scientific Advancement',
        ranked='Most Scientifically Advanced',
        measurement='Kurzweil Singularity Index',
        image='advanced',
        nation_description=('World Census researchers quantified national '
                            'scientific advancement by quizzing random '
                            'citizens about quantum chromodynamics, '
                            'space-time curvature and stem cell '
                            'rejuvenation therapies. Responses based on '
                            'Star Trek were discarded.'),
        region_description=('World Census researchers quantified regional '
                            'scientific advancement by quizzing random '
                            'citizens about quantum chromodynamics, '
                            'space-time curvature and stem cell '
                            'rejuvenation therapies. Responses based on '
                            'Star Trek were discarded.'),
    ),
    71: ScaleInfo(
        id=71,
        title='Inclusiveness',
        ranked='Most Inclusive',
        measurement='Mandela-Wollstonecraft Non-Discrimination Index',
        image='inclusive',
        nation_description=('WA analysts ranked nations based on whether '
                            'all citizens were commonly treated as equally '
                            'valuable members of society.'),
        region_description=('WA analysts ranked regions based on whether '
                            'all citizens were commonly treated as equally '
                            'valuable members of society.'),
    ),
    72: ScaleInfo(
        id=72,
        title='Average Income',
        ranked='Highest Average Incomes',
        measurement='Standard Monetary Units',
        image='income',
        nation_description=('The World Census carefully compared the '
                            'average spending power of citizens in each '
                            'nation.'),
        region_description=('The World Census carefully compared the '
                            'average spending power of citizens in each '
                            'region.'),
    ),
    73: ScaleInfo(
        id=73,
        title='Average Income of Poor',
        ranked='Highest Poor Incomes',
        measurement='Standard Monetary Units',
        image='poorincome',
        nation_description=('The World Census studied the spending power '
                            'of the poorest 10% of citizens in each nation.'),
        region_description=('The World Census studied the spending power '
                            'of the poorest 10% of citizens in each region.'),
    ),
    74: ScaleInfo(
        id=74,
        title='Average Income of Rich',
        ranked='Highest Wealthy Incomes',
        measurement='Standard Monetary Units',
        image='richincome',
        nation_description=('The World Census studied the spending power '
                            'of the richest 10% of citizens in each nation.'),
        region_description=('The World Census studied the spending power '
                            'of the richest 10% of citizens in each region.'),
    ),
    75: ScaleInfo(
        id=75,
        title='Public Education',
        ranked='Most Advanced Public Education',
        measurement='Edu-tellignce\u00AE Test Score',
        image='educated',
        nation_description=('Fresh-faced World Census agents infiltrated '
                            'schools with varying degrees of success in '
                            'order to determine which nations had the most '
                            'widespread, well-funded, and advanced public '
                            'education programs.'),
        region_description=('Fresh-faced World Census agents infiltrated '
                            'schools with varying degrees of success in '
                            'order to determine which regions had the most '
                            'widespread, well-funded, and advanced public '
                            'education programs.'),
    ),
    76: ScaleInfo(
        id=76,
        title='Economic Output',
        ranked='Highest Economic Output',
        measurement='Standard Monetary Units',
        image='gdp',
        nation_description=('World Census bean-counters crunched the '
                            'numbers to calculate national Gross Domestic '
                            'Product. Older nations, with higher '
                            'populations, were noted to have a distinct '
                            'advantage.'),
        region_description=('World Census bean-counters crunched the '
                            'numbers to calculate regional Gross Domestic '
                            'Product. Older regions, with higher '
                            'populations, were noted to have a distinct '
                            'advantage.'),
    ),
    77: ScaleInfo(
        id=77,
        title='Crime',
        ranked='Highest Crime Rates',
        measurement='Crimes Per Hour',
        image='crime',
        nation_description=('World Census interns were dispatched to seedy '
                            'back alleys in order to determine which '
                            'nations have the highest crime rates.'),
        region_description=('World Census interns were dispatched to seedy '
                            'back alleys in order to determine which '
                            'regions have the highest crime rates.'),
    ),
    78: ScaleInfo(
        id=78,
        title='Foreign Aid',
        ranked='Highest Foreign Aid Spending',
        measurement='Clooney Contribution Index',
        image='aid',
        nation_description=('The World Census intercepted food drops in '
                            'several war-torn regions to determine which '
                            'nations spent the most on international aid. '),
        region_description=('The World Census intercepted food drops in '
                            'several war-torn regions to determine which '
                            'regions spent the most on international aid. '),
    ),
    79: ScaleInfo(
        id=79,
        title='Black Market',
        ranked='Largest Black Market',
        measurement='Standard Monetary Units',
        image='blackmarket',
        nation_description=('World Census agents tracked "off the books" '
                            'deals and handshake agreements in order to '
                            "study the size of nations' informal economies."),
        region_description=('World Census agents tracked "off the books" '
                            'deals and handshake agreements in order to '
                            "study the size of regions' informal economies."),
    ),
    80: ScaleInfo(
        id=80,
        title='Residency',
        ranked='Most Stationary',
        measurement='Days',
        image='stationary',
        nation_description=('Long-term World Census surveillance revealed '
                            'which nations have been resident in their '
                            'current region for the longest time.'),
        region_description=('Long-term World Census surveillance revealed '
                            'which regions have the most physically '
                            'grounded nations.'),
    ),
}


class Banner:
    """A Rift banner.

    Attributes
    ----------
    id : int
        The banner id.
    name : str
        The banner name.
    validity : str
        A requirement the nation has to meet in order to get the banner.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def url(self):
        """Link to the banner image."""
        return banner_url(self.id)

    async def _expand_macros(self, expand_macros):
        return self._replace(
            name=await expand_macros(self.name),
            validity=await expand_macros(self.validity)
        )


def banner(id):
    try:
        return banner_info[id]
    except KeyError:
        return Banner(
            id=id,
            name='Custom',
            validity='Reach a certain population threshold'
        )


banner_info = {
    'a1': Banner(
        id='a1',
        name='Chewing the Cud',
        validity='Prioritize agriculture-based industries',
    ),
    'a2': Banner(
        id='a2',
        name='Rush Hour',
        validity='Develop a strong cattle industry',
    ),
    'a3': Banner(
        id='a3',
        name='Productive Soil',
        validity=('Develop a strong agriculture sector alongside a good '
                  'environment'),
    ),
    'a4': Banner(
        id='a4',
        name='Early to Rise',
        validity='Develop a thriving agriculture sector',
    ),
    'a5': Banner(
        id='a5',
        name='From the Earth',
        validity='Enforce compulsory vegetarianism',
    ),
    'a6': Banner(
        id='a6',
        name='On the Menu',
        validity='Eat your national animal',
    ),
    'b1': Banner(
        id='b1',
        name='Air and Glass',
        validity=("Develop a technologically literate populace that doesn't "
                  'care that much'),
    ),
    'b2': Banner(
        id='b2',
        name='Modern Style',
        validity='Develop clever citizens',
    ),
    'b3': Banner(
        id='b3',
        name='Minimalist Curves',
        validity='Develop an extremely intelligent populace',
    ),
    'b4': Banner(
        id='b4',
        name='Interior Tech',
        validity='Combine a strong IT industry with a powerhouse economy',
    ),
    'b5': Banner(
        id='b5',
        name='Server Room',
        validity='Develop a strong technology industry',
    ),
    'b6': Banner(
        id='b6',
        name='Domed',
        validity='Develop excellent political freedoms',
    ),
    'b7': Banner(
        id='b7',
        name='Leadership',
        validity='Take charge',
    ),
    'b8': Banner(
        id='b8',
        name='Department of Oversight',
        validity='Clamp down on political freedom',
    ),
    'b9': Banner(
        id='b9',
        name='Removed',
        validity='Develop a religious yet uncaring populace',
    ),
    'b10': Banner(
        id='b10',
        name="You Didn't Build That",
        validity='Engage in corporate welfare',
    ),
    'b11': Banner(
        id='b11',
        name='Business First',
        validity='Prioritize commerce',
    ),
    'b12': Banner(
        id='b12',
        name='Cold Hard Reality',
        validity='Eliminate public healthcare',
    ),
    'b13': Banner(
        id='b13',
        name='Secure',
        validity='Fill the prisons',
    ),
    'b14': Banner(
        id='b14',
        name='Needs of the Many',
        validity='Enforce capital punishment',
    ),
    'b15': Banner(
        id='b15',
        name='Dissent is Treason',
        validity='Harshly suppress political opposition',
    ),
    'b16': Banner(
        id='b16',
        name='Medieval',
        validity='Reject modern ways',
    ),
    'b17': Banner(
        id='b17',
        name='Nice for Some',
        validity=('Simultaneously develop a strong economy and high income '
                  'inequality'),
    ),
    'b18': Banner(
        id='b18',
        name='Contemplation',
        validity='Develop a faithful populace',
    ),
    'b19': Banner(
        id='b19',
        name='Between God and Rock',
        validity='Provide significant public funding for religion',
    ),
    'b20': Banner(
        id='b20',
        name='Hallowed Halls',
        validity='Support traditional religion',
    ),
    'b21': Banner(
        id='b21',
        name='Stadium',
        validity='Develop healthy citizens',
    ),
    'b22': Banner(
        id='b22',
        name='Gatekeepers',
        validity='Develop high levels of corruption',
    ),
    'b23': Banner(
        id='b23',
        name='Palatial',
        validity='Develop very high levels of corruption',
    ),
    'b24': Banner(
        id='b24',
        name='Listening In',
        validity='Take a keen interest in what your citizens are doing',
    ),
    'b25': Banner(
        id='b25',
        name='Perspective',
        validity='Believe in religious tolerance',
    ),
    'c1': Banner(
        id='c1',
        name='Bright Lights, Big City',
        validity='Combine 1 billion citizens with a very strong economy',
    ),
    'c2': Banner(
        id='c2',
        name='River City',
        validity='Combine 100 million citizens with a reasonable economy',
    ),
    'c3': Banner(
        id='c3',
        name='Metropolis',
        validity='Combine 400 million citizens with a good economy',
    ),
    'c4': Banner(
        id='c4',
        name='Incremental Improvement',
        validity=('Develop a good economy in a nation of at least 200 '
                  'million citizens'),
    ),
    'c5': Banner(
        id='c5',
        name='Fast Lane',
        validity='Choose cars over environment',
    ),
    'c6': Banner(
        id='c6',
        name='Modern Steel',
        validity=('Reach 100 million citizens with an excellent environment '
                  'and economy'),
    ),
    'c7': Banner(
        id='c7',
        name='Progress is Movement',
        validity='Develop a thriving gambling industry',
    ),
    'c8': Banner(
        id='c8',
        name='City of Sand',
        validity=('Combine a population of 200 million with a terrible '
                  'environment'),
    ),
    'c9': Banner(
        id='c9',
        name='Aspire',
        validity=('Develop a strong economy in a scientifically advanced '
                  'nation with a good environment'),
    ),
    'c10': Banner(
        id='c10',
        name='Progress is Thirsty Work',
        validity='Develop a strong economy in a collapsing environment',
    ),
    'c11': Banner(
        id='c11',
        name="Renovator's Delight",
        validity='Combine 100 million citizens with a weak economy',
    ),
    'c12': Banner(
        id='c12',
        name='Urban Sprawl',
        validity='Reach 5 billion citizens',
    ),
    'c13': Banner(
        id='c13',
        name="Artist's Impression",
        validity=('Develop high levels of economic freedom in a nation of '
                  'at least 250 million citizens'),
    ),
    'c14': Banner(
        id='c14',
        name='Island of Many Hills',
        validity=('Develop a very strong economy in a nation of 2 '
                  'billion citizens'),
    ),
    'c15': Banner(
        id='c15',
        name='Mega-Metropolis',
        validity='Combine 10 billion citizens with a powerhouse economy',
    ),
    'c16': Banner(
        id='c16',
        name='Power Grid',
        validity='Boost education',
    ),
    'c17': Banner(
        id='c17',
        name='Skyward',
        validity='Reach 500 million citizens with a very strong economy',
    ),
    'c18': Banner(
        id='c18',
        name='Steel and Glass',
        validity='Reach 2 billion citizens with a strong economy',
    ),
    'c19': Banner(
        id='c19',
        name='Beating Heart',
        validity=('Reach 300 million citizens with a very strong economy and '
                  'a non-terrible environment'),
    ),
    'c20': Banner(
        id='c20',
        name='No Limits',
        validity='Abolish speed limits',
    ),
    'c21': Banner(
        id='c21',
        name='They Grow Up So Fast',
        validity='Develop a good economy in a nation of 300 million citizens',
    ),
    'd1': Banner(
        id='d1',
        name='Slight Crime Problem',
        validity=('Develop a crippling crime problem in a reasonably '
                  'wealthy nation of at least 500 million citizens'),
    ),
    'd2': Banner(
        id='d2',
        name='Bridge to Nowhere',
        validity='Overlook education',
    ),
    'd3': Banner(
        id='d3',
        name='Exodus',
        validity='Combine a terrible economy with a terrible environment',
    ),
    'd4': Banner(
        id='d4',
        name="Not Sure What's Happening Here",
        validity='Be strange',
    ),
    'd5': Banner(
        id='d5',
        name='Could Have Happened to Anyone',
        validity='Combine sub-par intelligence with a beautiful environment',
    ),
    'd6': Banner(
        id='d6',
        name='White Whale',
        validity='Fail to prevent mistakes in the fishing industry',
    ),
    'd7': Banner(
        id='d7',
        name='Inconsistent Service Delivery',
        validity='Abolish the government',
    ),
    'e1': Banner(
        id='e1',
        name='Ride the Wave',
        validity='Trust the market',
    ),
    'e2': Banner(
        id='e2',
        name='Open for Business',
        validity='Help your people do business',
    ),
    'e3': Banner(
        id='e3',
        name='Conference',
        validity='Partner with private industry',
    ),
    'e4': Banner(
        id='e4',
        name='Making No Cents',
        validity='Free yourself from the tyranny of coins',
    ),
    'e5': Banner(
        id='e5',
        name='All That Glitters',
        validity=('Combine a thriving economy with significant corruption '
                  'and inequality'),
    ),
    'f1': Banner(
        id='f1',
        name='Misty Morning',
        validity='Protect the forests',
    ),
    'f2': Banner(
        id='f2',
        name='Treefall',
        validity='Protect the land',
    ),
    'f3': Banner(
        id='f3',
        name='Autumnal',
        validity='See in your first national birthday',
    ),
    'f4': Banner(
        id='f4',
        name='Happy Trails',
        validity='Address 200 issues',
    ),
    'f5': Banner(
        id='f5',
        name='Tall Timber',
        validity='Develop a thriving timber industry',
    ),
    'g1': Banner(
        id='g1',
        name='Form and Function',
        validity='Guide the political process with a firm hand',
    ),
    'g2': Banner(
        id='g2',
        name='Glory to the Government',
        validity='Develop a large, corrupt government',
    ),
    'g3': Banner(
        id='g3',
        name='Pillar of Society',
        validity='Grow the government',
    ),
    'h1': Banner(
        id='h1',
        name='Cracked',
        validity='Have trouble attracting tourists',
    ),
    'h2': Banner(
        id='h2',
        name='Dune',
        validity='Enhance the environment by removing trees',
    ),
    'i1': Banner(
        id='i1',
        name='Model of Efficiency',
        validity='Prioritize the economy over the environment',
    ),
    'i2': Banner(
        id='i2',
        name='Energy Source',
        validity='Power the economy without mining',
    ),
    'i3': Banner(
        id='i3',
        name='Clean and Green',
        validity='Fund environmental initiatives',
    ),
    'i4': Banner(
        id='i4',
        name='Piped Profits',
        validity='Develop a thriving soda industry',
    ),
    'i5': Banner(
        id='i5',
        name='Engine of Growth',
        validity='Develop a strong automotive industry',
    ),
    'i6': Banner(
        id='i6',
        name='Trade Hub',
        validity='Develop a broad industrial base',
    ),
    'i7': Banner(
        id='i7',
        name='Export Sales',
        validity='Develop a thriving industry',
    ),
    'i8': Banner(
        id='i8',
        name='Live Wire',
        validity='Outsource national power generation',
    ),
    'i9': Banner(
        id='i9',
        name='Better When Bottled',
        validity='Develop a thriving bottled goods industry',
    ),
    'i10': Banner(
        id='i10',
        name='Vaults of Knowledge',
        validity='Develop a thriving publishing industry',
    ),
    'i11': Banner(
        id='i11',
        name='Gone Fission',
        validity='Build nuclear power plants',
    ),
    'i12': Banner(
        id='i12',
        name='Foundry',
        validity='Develop a solid industrial base',
    ),
    'i13': Banner(
        id='i13',
        name='Platform for Expansion',
        validity='Develop a very large industrial base',
    ),
    'i14': Banner(
        id='i14',
        name='The Hand That Feeds',
        validity=('Simultaneously develop strong automotive and '
                  'agricultural sectors'),
    ),
    'i15': Banner(
        id='i15',
        name='Conveyance',
        validity='Develop a strong transportation plan',
    ),
    'i16': Banner(
        id='i16',
        name='Jacked In',
        validity='Embrace technology',
    ),
    'i17': Banner(
        id='i17',
        name='Book Repository',
        validity='Develop quality libraries',
    ),
    'i18': Banner(
        id='i18',
        name='An Apple a Day',
        validity='Encourage healthy eating',
    ),
    'i19': Banner(
        id='i19',
        name='Railworks',
        validity='Maintain a healthy economy in the absence of cars',
    ),
    'i20': Banner(
        id='i20',
        name='Puffing Billy',
        validity='Provide low-tech public transport',
    ),
    'i21': Banner(
        id='i21',
        name='Book Smarts',
        validity='Develop a nation of readers',
    ),
    'i22': Banner(
        id='i22',
        name='Blue Sky Mining',
        validity='Develop a strong mining industry',
    ),
    'i23': Banner(
        id='i23',
        name='The Fish Are Worth It',
        validity='Support the fishing industry',
    ),
    'i24': Banner(
        id='i24',
        name='Delicious',
        validity='Support the dairy industry',
    ),
    'i25': Banner(
        id='i25',
        name='Slice of Life',
        validity='Support the pizza industry',
    ),
    'i26': Banner(
        id='i26',
        name='On Rails',
        validity='Provide substantial public transport',
    ),
    'k1': Banner(
        id='k1',
        name='Bike Lane',
        validity='Ban automobiles',
    ),
    'k2': Banner(
        id='k2',
        name='In My Sights',
        validity='Support the right to bear arms',
    ),
    'k3': Banner(
        id='k3',
        name='Protector',
        validity="Know what's best",
    ),
    'k4': Banner(
        id='k4',
        name='Holy Warriors',
        validity='Develop a faith-based military',
    ),
    'l1': Banner(
        id='l1',
        name='Red Dawn',
        validity='Revere a land-based animal',
    ),
    'l2': Banner(
        id='l2',
        name='Hilly Terrain',
        validity='Become a site supporter',
    ),
    'l3': Banner(
        id='l3',
        name='Every Road is a Story',
        validity='Write five or more dispatches or factbooks',
    ),
    'l4': Banner(
        id='l4',
        name='Some Climbing Required',
        validity='Write a Factbook',
    ),
    'l5': Banner(
        id='l5',
        name='Trespassers Will Be Prosecuted',
        validity='Close the borders to immigration',
    ),
    'l6': Banner(
        id='l6',
        name='Unbeaten Path',
        validity='Become an Anarchy',
    ),
    'l7': Banner(
        id='l7',
        name='Sand and Rock',
        validity=('Attribute 1% of annual deaths to people getting lost '
                  'in the wilderness '),
    ),
    'l8': Banner(
        id='l8',
        name='Sole Survivor',
        validity='Develop an extremely strong timber industry',
    ),
    'l9': Banner(
        id='l9',
        name='Tourist Destination',
        validity='Develop a culture-based tourism industry',
    ),
    'l10': Banner(
        id='l10',
        name='Revolving',
        validity='Explore alternative forms of energy',
    ),
    'l11': Banner(
        id='l11',
        name='Outdoor Pursuits',
        validity=('Combine a healthy populace, civil rights, and an '
                  'excellent environment'),
    ),
    'l12': Banner(
        id='l12',
        name='Hiking',
        validity=('Leverage a beautiful environment into a thriving '
                  'tourism industry'),
    ),
    'l13': Banner(
        id='l13',
        name='Abandoned',
        validity='Exhibit a disturbingly low average lifespan',
    ),
    'l14': Banner(
        id='l14',
        name='Brave New World',
        validity='Found a region',
    ),
    'l16': Banner(
        id='l16',
        name='Cavern',
        validity=('Give tourism a state-funded helping hand to promote an '
                  'excellent environment'),
    ),
    'l17': Banner(
        id='l17',
        name='Hostile Elements',
        validity=('Develop a nation of at least 50 million citizens who '
                  "aren't especially fond of strangers"),
    ),
    'l18': Banner(
        id='l18',
        name='Perched',
        validity='Divide into self-governing regions',
    ),
    'l19': Banner(
        id='l19',
        name='A New Day',
        validity='Change from one nation classification to another',
    ),
    'l20': Banner(
        id='l20',
        name='Fields of Gold',
        validity='Become a World Assembly Delegate',
    ),
    'l21': Banner(
        id='l21',
        name='Rock of Ages',
        validity='Be truly ancient',
    ),
    'l22': Banner(
        id='l22',
        name='Gray Power',
        validity='Care for the elderly',
    ),
    'l23': Banner(
        id='l23',
        name='Something Better',
        validity='Reject industry',
    ),
    'l24': Banner(
        id='l24',
        name='Oasis',
        validity='Be a regional hermit',
    ),
    'l25': Banner(
        id='l25',
        name='Remembered',
        validity='Push average citizen lifespan below 50 years',
    ),
    'l26': Banner(
        id='l26',
        name='At Rest',
        validity='Eliminate the elderly',
    ),
    'l28': Banner(
        id='l28',
        name='Seeing in the Dawn',
        validity='Develop a population of at least 6 million citizens',
    ),
    'l29': Banner(
        id='l29',
        name='Pause for Sightseeing',
        validity=('Combine a pleasant environment with cars and low '
                  'intelligence'),
    ),
    'l30': Banner(
        id='l30',
        name='Retirement',
        validity="Extend your citizens' average lifespan beyond 80 years",
    ),
    'l31': Banner(
        id='l31',
        name='Old Ways are Best',
        validity='Develop a low-tech but economically thriving nation',
    ),
    'l32': Banner(
        id='l32',
        name='Temperature Dropping',
        validity='Develop an inhospitable climate',
    ),
    'l33': Banner(
        id='l33',
        name="There's a Whole World Out Here",
        validity='Abolish computers',
    ),
    'l34': Banner(
        id='l34',
        name='Go It Alone',
        validity='Reject state-funded welfare',
    ),
    'l35': Banner(
        id='l35',
        name='Home Alone',
        validity='Develop a populace who like to keep to themselves',
    ),
    'l36': Banner(
        id='l36',
        name='Immortal',
        validity='Address 300 issues',
    ),
    'l37': Banner(
        id='l37',
        name='Rocky Endeavor',
        validity='Address 150 issues',
    ),
    'l38': Banner(
        id='l38',
        name='Windswept',
        validity='Address six issues',
    ),
    'l39': Banner(
        id='l39',
        name='Scenic Slag Heap',
        validity=('Develop a beautiful environment alongside a thriving '
                  'mining industry'),
    ),
    'l40': Banner(
        id='l40',
        name='Mesa',
        validity='Address 15 issues',
    ),
    'l41': Banner(
        id='l41',
        name='Life is a Mystery',
        validity='Cultivate a deeply spiritual populace',
    ),
    'l42': Banner(
        id='l42',
        name='Snowed In',
        validity='Address ten issues',
    ),
    'l43': Banner(
        id='l43',
        name='Stand Alone',
        validity='Eschew the military',
    ),
    'l44': Banner(
        id='l44',
        name='The Hills are Alive',
        validity=('Develop a beautiful environment in a nation of 1 '
                  'billion citizens'),
    ),
    'l45': Banner(
        id='l45',
        name='Cultivated',
        validity='Provide government support for parks and nature reserves',
    ),
    'm1': Banner(
        id='m1',
        name='Tanks for Everything',
        validity='Build a large military',
    ),
    'm2': Banner(
        id='m2',
        name='Sunset Escort',
        validity='Build a substantial military',
    ),
    'm3': Banner(
        id='m3',
        name="A Moment's Peace",
        validity='Combine a strong military with civil rights',
    ),
    'm4': Banner(
        id='m4',
        name='Cruise',
        validity='Build an extremely large military',
    ),
    'm5': Banner(
        id='m5',
        name='Patrol',
        validity='Build a ridiculously large military',
    ),
    'm6': Banner(
        id='m6',
        name='From Above',
        validity='Build a very large military',
    ),
    'm7': Banner(
        id='m7',
        name='Peacekeepers',
        validity='Build a military',
    ),
    'm8': Banner(
        id='m8',
        name='Material Disadvantage',
        validity='Build an inadequately-funded military',
    ),
    'n1': Banner(
        id='n1',
        name='Medical Innovation',
        validity='Fund advanced health research ',
    ),
    'n2': Banner(
        id='n2',
        name='Genetic Warfare',
        validity='Combine a strong military with advanced medical research',
    ),
    'n3': Banner(
        id='n3',
        name='Improvements Can Be Made',
        validity='Fund very advanced health research',
    ),
    'n4': Banner(
        id='n4',
        name='There Are Always More Questions',
        validity='Become highly scientifically advanced',
    ),
    'n5': Banner(
        id='n5',
        name='Budding Freedoms',
        validity='Develop high recreational drug use',
    ),
    'o1': Banner(
        id='o1',
        name='Very Fishy',
        validity='Revere a marine animal',
    ),
    'o2': Banner(
        id='o2',
        name='Homeward, with Ripples',
        validity='Develop a thriving tourism industry',
    ),
    'o3': Banner(
        id='o3',
        name='Ocean Nova',
        validity='Develop a world-class environment',
    ),
    'o4': Banner(
        id='o4',
        name='Crisp Morning',
        validity='Address 75 issues',
    ),
    'o5': Banner(
        id='o5',
        name='Respected',
        validity='Be endorsed',
    ),
    'o6': Banner(
        id='o6',
        name='Waking in Paradise',
        validity='Develop an extremely good environment',
    ),
    'o8': Banner(
        id='o8',
        name='Shacked Up',
        validity='Combine a good environment with below-average economy',
    ),
    'o9': Banner(
        id='o9',
        name='New Around Here',
        validity='Found a nation!',
    ),
    'o10': Banner(
        id='o10',
        name='Beached',
        validity=('Develop a compassionate populace in a nation with a '
                  'good environment'),
    ),
    'p1': Banner(
        id='p1',
        name='Mother and Child',
        validity='Eliminate youth crime while maintaining civil rights',
    ),
    'p2': Banner(
        id='p2',
        name='Faces of @@NAME@@ #1',
        validity='Develop above average civil rights',
    ),
    'p3': Banner(
        id='p3',
        name='Handheld',
        validity='Stay out of the bedroom',
    ),
    'p4': Banner(
        id='p4',
        name='@@DEMONYM@@ Fashion',
        validity='Develop a world-class fashion industry',
    ),
    'p5': Banner(
        id='p5',
        name='Faces of @@NAME@@ #6',
        validity='Develop superb civil rights',
    ),
    'p6': Banner(
        id='p6',
        name='Faces of @@NAME@@ #5',
        validity='Develop excellent civil rights',
    ),
    'p7': Banner(
        id='p7',
        name='Faces of @@NAME@@ #4',
        validity='Develop excellent civil rights',
    ),
    'p8': Banner(
        id='p8',
        name='Faces of @@NAME@@ #3',
        validity='Develop very good civil rights',
    ),
    'p9': Banner(
        id='p9',
        name='Faces of @@NAME@@ #2',
        validity='Develop very good civil rights',
    ),
    'p10': Banner(
        id='p10',
        name='Faces of @@NAME@@ #7',
        validity='Develop superb civil rights',
    ),
    'p11': Banner(
        id='p11',
        name='Faces of @@NAME@@ #8',
        validity='Develop world benchmark civil rights',
    ),
    'p12': Banner(
        id='p12',
        name='Faces of @@NAME@@ #9',
        validity='Develop world benchmark civil rights',
    ),
    'p13': Banner(
        id='p13',
        name='Faces of @@NAME@@ #10',
        validity='Develop world benchmark civil rights',
    ),
    'p14': Banner(
        id='p14',
        name='Faces of @@NAME@@ #11',
        validity='Develop excessive civil rights',
    ),
    'p15': Banner(
        id='p15',
        name='Faces of @@NAME@@ #12',
        validity='Develop excessive civil rights',
    ),
    'p16': Banner(
        id='p16',
        name='Faces of @@NAME@@ #13',
        validity='Develop frightening civil rights',
    ),
    'p17': Banner(
        id='p17',
        name='Power from the People',
        validity='Develop a keenly politically-aware populace',
    ),
    'p18': Banner(
        id='p18',
        name='Cheeky',
        validity='Take it all off',
    ),
    'p19': Banner(
        id='p19',
        name='Starting Out',
        validity='Combine civil rights with a healthy economy',
    ),
    'p20': Banner(
        id='p20',
        name='Ocean Frolics',
        validity='Make your people extremely cheerful',
    ),
    'p21': Banner(
        id='p21',
        name='Faces of @@NAME@@ #14',
        validity='Develop frightening civil rights',
    ),
    'p22': Banner(
        id='p22',
        name='Giving Back',
        validity="Extend your citizens' average lifespan beyond 70 years",
    ),
    'p23': Banner(
        id='p23',
        name='Popular Uprising',
        validity='Defend the right to protest',
    ),
    'p24': Banner(
        id='p24',
        name='Kickball',
        validity='Nurture a happy, free populace',
    ),
    'p25': Banner(
        id='p25',
        name='Together',
        validity='Share the institution of marriage',
    ),
    'p26': Banner(
        id='p26',
        name='Keeper of the Flame',
        validity='Support alternative religions',
    ),
    'q1': Banner(
        id='q1',
        name='Birds of a Feather',
        validity='Be endorsed by six nations at once',
    ),
    'r1': Banner(
        id='r1',
        name='Trickle Down',
        validity='Develop high income inequality',
    ),
    'r2': Banner(
        id='r2',
        name='Seen Much Better Days',
        validity='Run a very poor economy',
    ),
    'r3': Banner(
        id='r3',
        name='Slumming',
        validity='Develop significant numbers of impoverished citizens',
    ),
    'r4': Banner(
        id='r4',
        name='Small Business',
        validity='Run a fragile economy or worse',
    ),
    'r5': Banner(
        id='r5',
        name='Home',
        validity='Develop a good economy with some income inequality',
    ),
    'r6': Banner(
        id='r6',
        name='Seen Better Days',
        validity='Run a crumbling economy',
    ),
    'r7': Banner(
        id='r7',
        name='Stories to Tell',
        validity='Publish a dispatch other than a Factbook',
    ),
    'r8': Banner(
        id='r8',
        name='The Sea Remembers',
        validity="Make sewage waste someone else's problem",
    ),
    'r9': Banner(
        id='r9',
        name='Detrimental Externality',
        validity='Seriously prioritize the economy over the environment',
    ),
    'r10': Banner(
        id='r10',
        name='Dumped',
        validity='Eliminate environmental protections',
    ),
    'r11': Banner(
        id='r11',
        name='Nothing to See Here',
        validity='Develop a serious crime problem',
    ),
    's1': Banner(
        id='s1',
        name='Keeping the Peace',
        validity='Prioritize Law & Order',
    ),
    's2': Banner(
        id='s2',
        name='Thickening Blue Line',
        validity='Boost the police force',
    ),
    's3': Banner(
        id='s3',
        name='National Pride',
        validity='Enforce compulsory military service',
    ),
    't1': Banner(
        id='t1',
        name='All Available Space',
        validity='Run a below-average but not terrible economy',
    ),
    't2': Banner(
        id='t2',
        name='Vista',
        validity='Be cultured',
    ),
    't4': Banner(
        id='t4',
        name='The Other Way',
        validity='Develop a good economy without free markets',
    ),
    't5': Banner(
        id='t5',
        name='High-Density Culture',
        validity='Show an appreciation for the finer things',
    ),
    't6': Banner(
        id='t6',
        name='Light the Lamps',
        validity='Become influential in a region',
    ),
    't8': Banner(
        id='t8',
        name='Icy Gaze',
        validity='Address 250 issues',
    ),
    't9': Banner(
        id='t9',
        name='On the Water',
        validity='Prioritize the environment over the economy',
    ),
    't10': Banner(
        id='t10',
        name='Holy Water',
        validity='Support @@FAITH@@',
    ),
    't11': Banner(
        id='t11',
        name='Oversight',
        validity='Fund Law & Order in a low-tech nation',
    ),
    't12': Banner(
        id='t12',
        name='Under and Over',
        validity='Simultaneously develop low inequality and high culture',
    ),
    't13': Banner(
        id='t13',
        name='Tranquility',
        validity='Develop a pleasant environment in a religious nation',
    ),
    't14': Banner(
        id='t14',
        name='Queen of the Hill',
        validity='Address 30 issues',
    ),
    't15': Banner(
        id='t15',
        name='The Sun Always Rises',
        validity='Exhibit low unemployment',
    ),
    't16': Banner(
        id='t16',
        name='Morning Calm',
        validity='Achieve balance in all things',
    ),
    't17': Banner(
        id='t17',
        name='Seat of Power',
        validity='Develop a large, tasteful government',
    ),
    't18': Banner(
        id='t18',
        name='Summer Residence',
        validity=('Develop deep-rooted corruption with a taste for nice '
                  'things'),
    ),
    't19': Banner(
        id='t19',
        name='Father Knows Best',
        validity='Become a Father Knows Best state',
    ),
    't20': Banner(
        id='t20',
        name='Window Shopping',
        validity=('Develop a cultured nation of at least 80 million with '
                  'good civil rights'),
    ),
    't21': Banner(
        id='t21',
        name='Crisp Village',
        validity=('Develop a cultured, self-centered nation of at least 40 '
                  'million citizens'),
    ),
    't22': Banner(
        id='t22',
        name='A Many Splendored Land',
        validity='Address 50 issues',
    ),
    't23': Banner(
        id='t23',
        name='Simple Life',
        validity='Develop an issue with unemployment',
    ),
    't24': Banner(
        id='t24',
        name='City of Sticks',
        validity='Combine a beautiful environment with a weak economy',
    ),
    't25': Banner(
        id='t25',
        name='Above it All',
        validity='Develop a stoic, dispassionate citizenry',
    ),
    't26': Banner(
        id='t26',
        name='Green is the Morrow',
        validity='Address 100 issues',
    ),
    't27': Banner(
        id='t27',
        name='Nice Part of Town',
        validity='Get cultured',
    ),
    'u1': Banner(
        id='u1',
        name='No Rest for the Young',
        validity='Develop a problem with youth crime',
    ),
    'u2': Banner(
        id='u2',
        name='Underbelly',
        validity='Combine heavy industry with crime',
    ),
    'v1': Banner(
        id='v1',
        name='Celestial Color',
        validity='Embrace the one true faith',
    ),
    'w1': Banner(
        id='w1',
        name='No Moisture Required',
        validity='Have a truly terrible environment',
    ),
    'w2': Banner(
        id='w2',
        name='The Future is Near',
        validity='Make contact',
    ),
    'w3': Banner(
        id='w3',
        name='The Worlds Above Us',
        validity='Reach for the stars',
    ),
    'x1': Banner(
        id='x1',
        name='Out There',
        validity=("Become so technologically advanced, they don't even "
                  'have a name for it'),
    ),
    'x2': Banner(
        id='x2',
        name='Vats Entertainment',
        validity='Embrace vats',
    ),
    'x3': Banner(
        id='x3',
        name='There Will Be Blood',
        validity='Make sacrifices',
    ),
    'x4': Banner(
        id='x4',
        name='Atomic Age',
        validity='Build bigger bombs',
    ),
    'x5': Banner(
        id='x5',
        name='Infected',
        validity='Deal with the undead',
    ),
    'x6': Banner(
        id='x6',
        name='Avast!',
        validity='Keel-haul scurvy dogs',
    ),
    'z1': Banner(
        id='z1',
        name='Great Works',
        validity='Be cultured and clever',
    ),
    'z2': Banner(
        id='z2',
        name='Defiance',
        validity='Cultivate a nation of activists',
    ),
}
