from full_node_client import FullNodeClient

if __name__ == '__main__':
    full_node_client = FullNodeClient(
        '/',
        'rpcs.9swap.cyou:8880/',
        port=None,
        https=False
    )
    print(full_node_client)
    print(full_node_client.getBlockchainState())
