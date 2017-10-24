from enum import Enum


class RequestType(Enum):
    authorize = 'AuthorizeTransaction, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    authorize_and_capture = 'AuthorizeAndCaptureTransaction, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    manage_account = 'ManageAccount, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    adjust = 'Adjust, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    undo = 'Undo,http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    capture = 'Capture,http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    resubmit = 'ResubmitTransaction, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    capture_selective = 'CaptureSelective, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    capture_all = 'CaptureAll, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    return_by_id = 'ReturnById, http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'
    return_unlinked = 'ReturnTransaction,http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest'


class TransactionType(Enum):
    bankcard = 'BankcardTransaction,http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard'
    bankcard_profile = 'BankcardTransactionPro,http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard/Pro'
    electronic_checking = 'ElectronicCheckingTransaction, http://schemas.evosnap.com/CWS/v2.0/Transactions/ElectronicChecking'
    stored_value = 'StoredValueTransaction, http://schemas.evosnap.com/CWS/v2.0/Transactions/StoredValueTransaction'
    encryption = 'EncryptionTransaction, http://schemas.evosnap.com/CWS/v2.0/Transactions/EncryptionTransaction'


class TransactionDataType(Enum):
    bankcard = 'BankcardTransactionDataPro, http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard/Pro'
    electronic_checking = 'ElectronicCheckingTransactionData, http://schemas.evosnap.com/CWS/v2.0/Transactions/ElectronicChecking'


class CardType(Enum):
    american_express = 'AmericanExpress'
    carte_aurore = 'CarteAurore'
    cartes_bancaires = 'CartesBancaires'
    citibank_financial = 'CitibankFinancial'
    dankort = 'Dankort'
    diners_club = 'DinersClub'
    discover = 'Discover'
    electron = 'Electron'
    finax = 'Finax'
    jcb = 'JCB'
    kopkort = 'Kopkort'
    laser_card = 'LaserCard'
    maestro = 'Maestro'
    master_card = 'MasterCard'
    not_set = 'NotSet'
    private_label = 'PrivateLabel'
    revolution_card = 'RevolutionCard'
    solo = 'Solo'
    unbranded_atm = 'UnbrandedATM'
    visa = 'Visa'


class GoodsType(Enum):
    digital = 'DigitalGoods'
    not_set = 'NotSet'
    physical = 'PhysicalGoods'


class CustomerPresent(Enum):
    bill_payment = 'BillPayment'
    ecommerce = 'Ecommerce'
    mail_fax = 'MailFax'
    moto = 'MOTO'
    motocc = 'MOTOCC'
    not_set = 'NotSet'
    present = 'Present'
    suspicious = 'Suspicious'
    tel_aru = 'TelARU'
    transponder = 'Transponder'
    visa_unreadable = 'VisaCardPresentStripeUnreadable'
    visa_open_network = 'VisaOpenNetworkTransaction'
    voice_response = 'VoiceResponse'


class IndustryType(Enum):
    ecommerce = 'Ecommerce'
    moto = 'MOTO'
    not_set = 'NotSet'
    restaurant = 'Restaurant'
    retail = 'Retail'


class EntryMode(Enum):
    barcode = 'Barcode'
    chip_reliable = 'ChipReliable'
    chip_track_data_rfid = 'ChipTrackDataFromRFID'
    chip_unreliable = 'ChipUnreliable'
    contactless_chip_or_card = 'ContactlessMChipOrSmartCard'
    contactless_stripe = 'ContactlessStripe'
    keyed = 'Keyed'
    keyed_bad_read = 'KeyedBadMagRead'
    msrt_track_data_rfid = 'MSRTrackDataFromRFID'
    nfc_capable = 'NFCCapable'
    not_set = 'NotSet'
    ocr_reader = 'OCRReader'
    terminal_not_used = 'TerminalNotUsed'
    track2_data_msr = 'Track2DataFromMSR'
    track_data_msr = 'TrackDataFromMSR'
    vsc_capable = 'VSCCapable'


class AccountType(Enum):
    checking = 'CheckingAccount'
    not_set = 'NotSet'
    savings = 'SavingsAccount'


class CVDataProvided(Enum):
    not_available = 'CardholderStatesNotAvailable'
    bypass = 'DeliberatelyBypass'
    not_set = 'NotSet'
    provided = 'Provided'
    illegible = 'ValueIllegible'


class TokenIndicator(Enum):
    attempted_service_unsupported = 'AttemptedCardUnsupported'
    attempted_service_unavailable = 'AttemptedServiceUnavailable'
    not_set = 'NotSet'
    ucaf_with_data = 'UCAFWithData'
    ucaf_without_data = 'UCAFWithoutData'
    vpas = 'VPAS'


class ChargeType(Enum):
    beauty_shop = 'BeautyShop'
    conventional_fee = 'ConventionFee'
    gift_shop = 'GiftShop'
    golf_pro_shop = 'GolfProShop'
    health_spa = 'HealthSpa'
    lodging = 'Lodging'
    not_set = 'NotSet'
    restaurant = 'Restaurant'
    retail_other = 'RetailOther'
    tennis_pro_shop = 'TennisProShop'


class PINDebitUndoReason(Enum):
    cad_failure = 'CADFailure'
    customer_cancellation = 'CustomerCancellation'
    late_response = 'LateResponse'
    no_response = 'NoResponse'
    not_applicable = 'NotApplicable'
    not_set = 'NotSet'
    original_amount_incorrect = 'OriginalAmountIncorrect'
    partially_completed = 'PartiallyCompleted'
    response_incorrect = 'ResponseIncomplete'
    response_timeout = 'ResponseTimeout'
    suspect_malfunction = 'SuspectMalfunction'
    unable_to_deliver_response = 'UnableToDeliverResponse'
    unable_to_deliver_to_pos = 'UnableToDeliverToPOS'


class UndoReason(Enum):
    customer_cancellation = 'CustomerCancellation'
    not_set = 'NotSet'
