from enum import Enum


class DeviceType(Enum):
    
    None_               = 0x00

    DroneMain           = 0x01      # 드론 제어
    DroneSub            = 0x02      # 드론 통신
    Link                = 0x03      # 링크 모듈
    Tester              = 0x04      # 테스터

    EndOfType           = 0x05



class ImageType(Enum):

    None_                   = 0x00

    # 현재 장치의 이미지
    ImageA                  = 0x01
    ImageB                  = 0x02

    # 펌웨어 이미지
    RawImageA               = 0x03
    RawImageB               = 0x04

    EncryptedImageA         = 0x05
    EncryptedImageB         = 0x06

    # 현재 장치의 이미지(CC253x / CC254x)
    ImageSingle             = 0x07      # 실행 이미지

    # 현재 장치의 이미지(CC253x / CC254x)
    RawImageSingle          = 0x08      # 업데이트 이미지, 헤더 포함
    EncryptedImageSingle    = 0x09      # 업데이트 이미지, 헤더 포함

    EndOfType               = 0x0A



class ModeSystem(Enum):
    
    None_               = 0x00

    Boot                = 0x01      # 부팅
    Wait                = 0x02      # 연결 대기 상태

    Ready               = 0x03      # 대기 상태

    Running             = 0x04      # 메인 코드 동작

    Update              = 0x05      # 펌웨어 업데이트
    UpdateComplete      = 0x06      # 펌웨어 업데이트 완료

    Error               = 0x07      # 펌웨어 업데이트 완료

    EndOfType           = 0x08



class ModeVehicle(Enum):
    
    None_               = 0x00

    FlightGuard         = 0x10
    FlightNoGuard       = 0x11
    FlightFPV           = 0x12

    Drive               = 0x20
    DriveFPV            = 0x21

    Test                = 0x30

    EndOfType           = 0x31



class ModeFlight(Enum):
    
    None_               = 0x00

    Ready               = 0x01      # 비행 준비

    TakeOff             = 0x02      # 이륙 (Flight로 자동전환)
    Flight              = 0x03      # 비행
    Flip                = 0x04
    Stop                = 0x05      # 강제 정지
    Landing             = 0x06      # 착륙
    Reverse             = 0x07      # 뒤집기

    Accident            = 0x08      # 사고 (Ready로 자동전환)
    Error               = 0x09      # 오류

    EndOfType           = 0x0A



class ModeDrive(Enum):
    
    None_               = 0x00

    Ready               = 0x01      # 준비

    Start               = 0x02      # 출발
    Drive               = 0x03      # 주행
    Stop                = 0x04      # 강제 정지

    Accident            = 0x05      # 사고 (Ready로 자동전환)
    Error               = 0x06      # 오류

    EndOfType           = 0x07



class ModeUpdate(Enum):
    
    None_               = 0x00

    Ready               = 0x01      # 업데이트 가능 상태
    Update              = 0x02      # 업데이트 중
    Complete            = 0x03      # 업데이트 완료

    Faild               = 0x04      # 업데이트 실패(업데이트 완료까지 갔으나 body의 CRC16이 일치하지 않는 경우 등)

    EndOfType           = 0x05



class ModeLink(Enum):
    
    None_               = 0x00

    Boot                = 0x01      # 부팅
    Ready               = 0x02      # 대기(연결 전)
    Connecting          = 0x03      # 장치 연결 중
    Connected           = 0x04      # 장치 연결 완료(정상 연결 됨)
    Disconnecting       = 0x05      # 장치 연결 해제 중

    ReadyToReset        = 0x06      # 리셋 대기(1초 뒤 리셋)

    EndOfType           = 0x07



class ModeLinkBroadcast(Enum):
    
    None_               = 0x00

    Mute                = 0x01      # 데이터 송신 중단
    Active              = 0x02      # 요청한 데이터 이외에도 능동적으로 데이터 전송
    Passive             = 0x03      # 요청한 데이터에 대해서만 응답 - 상태 변경 시 상태 데이터 전송 없음, 연결 등의 상황에서는 진행 상황 전송
    
    EndOfType           = 0x07



class EventLink(Enum):
    None_                               = 0x00  # 없음

    SystemReset                         = 0x01  # 시스템 리셋

    Initialized                         = 0x02  # 장치 초기화 완료

    Scanning                            = 0x03  # 장치 검색 시작
    ScanStop                            = 0x04  # 장치 검색 중단

    FoundDroneService                   = 0x05  # 드론 서비스 검색 완료

    Connecting                          = 0x06  # 장치 연결 시작		
    Connected                           = 0x07  # 장치 연결

    ConnectionFaild                     = 0x08  # 연결 실패
    ConnectionFaildNoDevices            = 0x09  # 연결 실패 - 장치가 없음
    ConnectionFaildNotReady             = 0x0A  # 연결 실패 - 대기 상태가 아님

    PairingStart                        = 0x0B  # 페어링 시작
    PairingSuccess                      = 0x0C  # 페어링 성공
    PairingFaild                        = 0x0D  # 페어링 실패

    BondingSuccess                      = 0x0E  # Bonding 성공

    LookupAttribute                     = 0x0F  # 장치 서비스 및 속성 검색(GATT Event 실행)

    RssiPollingStart                    = 0x10  # RSSI 풀링 시작
    RssiPollingStop                     = 0x11  # RSSI 풀링 중지

    DiscoverService                     = 0x12  # 서비스 검색
    DiscoverCharacteristic              = 0x13  # 속성 검색
    DiscoverCharacteristicDroneData     = 0x14  # 속성 검색
    DiscoverCharacteristicDroneConfig   = 0x15  # 속성 검색
    DiscoverCharacteristicUnknown       = 0x16  # 속성 검색
    DiscoverCCCD                        = 0x17  # CCCD 검색

    ReadyToControl                      = 0x18  # 제어 준비 완료

    Disconnecting                       = 0x19  # 장치 연결 해제 시작
    Disconnected                        = 0x1A  # 장치 연결 해제 완료

    GapLinkParamUpdate                  = 0x1B  # GAP_LINK_PARAM_UPDATE_EVENT

    RspReadError                        = 0x1C  # RSP 읽기 오류
    RspReadSuccess                      = 0x1D  # RSP 읽기 성공

    RspWriteError                       = 0x1E  # RSP 쓰기 오류
    RspWriteSuccess                     = 0x1F  # RSP 쓰기 성공

    SetNotify                           = 0x20  # Notify 활성화

    Write                               = 0x21 # 데이터 쓰기 이벤트

    EndOfType                           = 0x22 



class ModeLinkDiscover(Enum):
    None_               = 0x00      

    Name                = 0x01      # 이름을 기준으로 검색
    Service             = 0x02      # 서비스를 기준으로 검색
    All                 = 0x03      # 모든 장치 검색

    EndOfType           = 0x04      



class FlightEvent(Enum):
    
    None_               = 0x00

    TakeOff             = 0x01      # 이륙

    FlipFront           = 0x02      # Reserved
    FlipRear            = 0x03      # Reserved
    FlipLeft            = 0x04      # Reserved
    FlipRight           = 0x05      # Reserved

    Stop                = 0x06      # 정지
    Landing             = 0x07      # 착륙
    Reverse             = 0x08      # 뒤집기

    Shot                = 0x09      # 미사일 쏠때 움직임
    UnderAttack         = 0x0A      # 미사일 맞을때 움직임

    EndOfType           = 0x0B



class DriveEvent(Enum):
    
    None_               = 0x00

    Stop                = 0x01
    
    Shot                = 0x02
    UnderAttack         = 0x03

    EndOfType           = 0x04



class Direction(Enum):
    
    None_               = 0x00

    Left                = 0x01
    Front               = 0x02
    Right               = 0x03
    Rear                = 0x04

    Top                 = 0x05
    Bottom              = 0x06

    EndOfType           = 0x07



class SensorOrientation(Enum):
    
    None_               = 0x00

    Normal              = 0x01
    ReverseStart        = 0x02
    Reversed            = 0x03

    EndOfType           = 0x04



class Headless(Enum):
    
    None_               = 0x00

    Headless            = 0x01      # Headless
    Normal              = 0x02      # Normal

    EndOfType           = 0x03



class Trim(Enum):
    
    None_               = 0x00  # 없음

    RollIncrease        = 0x01  # Roll 증가
    RollDecrease        = 0x02  # Roll 감소
    PitchIncrease       = 0x03  # Pitch 증가
    PitchDecrease       = 0x04  # Pitch 감소
    YawIncrease         = 0x05  # Yaw 증가
    YawDecrease         = 0x06  # Yaw 감소
    ThrottleIncrease    = 0x07  # Throttle 증가
    ThrottleDecrease    = 0x08  # Throttle 감소

    Reset               = 0x09  # 전체 트림 리셋

    EndOfType           = 0x0A


