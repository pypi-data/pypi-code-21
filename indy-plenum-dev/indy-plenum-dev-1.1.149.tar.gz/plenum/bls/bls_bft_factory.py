from common.serializers.serialization import multi_sig_store_serializer
from crypto.bls.bls_bft_replica import BlsBftReplica
from crypto.bls.bls_factory import BlsFactoryBft, BlsFactoryCrypto
from crypto.bls.bls_key_register import BlsKeyRegister
from plenum.bls.bls_bft_replica_plenum import BlsBftReplicaPlenum
from plenum.bls.bls_crypto_factory import create_default_bls_crypto_factory
from plenum.bls.bls_key_register_pool_manager import BlsKeyRegisterPoolManager
from plenum.bls.bls_store import BlsStore


class BlsFactoryBftPlenum(BlsFactoryBft):
    def __init__(self, bls_factory_crypto: BlsFactoryCrypto, node):
        super().__init__(bls_factory_crypto)
        self._node = node

    def create_bls_store(self):
        return BlsStore(key_value_type=self._node.config.stateSignatureStorage,
                        data_location=self._node.dataLocation,
                        key_value_storage_name=self._node.config.stateSignatureDbName,
                        serializer=multi_sig_store_serializer)

    def create_bls_key_register(self) -> BlsKeyRegister:
        return BlsKeyRegisterPoolManager(self._node.poolManager)

    def create_bls_bft_replica(self, is_master) -> BlsBftReplica:
        return BlsBftReplicaPlenum(self._node.name,
                                   self._node.bls_bft,
                                   is_master)


def create_default_bls_bft_factory(node):
    '''
    Creates a default BLS factory to instantiate BLS BFT classes.

    :param node: Node instance
    :return: BLS factory instance
    '''
    bls_crypto_factory = create_default_bls_crypto_factory(node.basedirpath,
                                                           node.name)
    return BlsFactoryBftPlenum(bls_crypto_factory,
                               node)
