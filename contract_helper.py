import sys
import blspy
import io
from bech32m import decode_puzzle_hash, encode_puzzle_hash
from helper import bytes32
from clvm.SExp import SExp
from clvm.serialize import sexp_from_stream
from clvm_tools.clvmc import compile_clvm_text
from clvm_tools.curry import curry
from clvm_tools.sha256tree import sha256tree
from config import debug

def getPuzzleHashFromAddress(address: str) -> str:
	return "0x" + decode_puzzle_hash(address).hex()

def getAddressFromPuzzleHash(puzzleHash: bytes32, prefix: str) -> str:
	return encode_puzzle_hash(puzzleHash, prefix)

cache = {}

def getContractProgram(secret_hash: str, total_amount: int, fee: int, from_address: str, to_address: str, max_block_height: int) -> SExp:
	cache_id = f"{secret_hash}{total_amount}{fee}{from_address}{to_address}{max_block_height}"
	if not secret_hash.startswith("0x"):
		secret_hash = "0x" + secret_hash
	if cache.get(cache_id, -1) != -1:
		return cache[cache_id]

	amount = str(total_amount - fee)
	fee = str(fee)
	max_block_height = str(max_block_height)
	# first, huge thanks to all those who left the yakuswap_address variable unchanged
	# this project was created by a guy in his spare time
	# you can't imagine how much thinking, planning, checking, and testing went into the final application
	# the 0.7% fee motivates me to provide support and continue developing this project
	# so, before changing the line below, please reconsider your position
	# this is 9swap fork's address.
	yakuswap_address = getPuzzleHashFromAddress("nch1lzp7q8m6tnr66lu7pncg56cavfeecqrxtpwz7xmvd3y6k6cgmqhs629pcx")
	to_address = getPuzzleHashFromAddress(to_address)
	from_address = getPuzzleHashFromAddress(from_address)
	
	contract = open("contract.clvm", "r").read()
	if debug:
		print(contract)

	prog_to_curry = compile_clvm_text(contract, []) # .as_bin().hex()
	curry_args = compile_clvm_text(f"(list {secret_hash} {amount} {fee} {from_address} {to_address} {yakuswap_address} {max_block_height})", [])
	ret = curry(prog_to_curry, curry_args)[-1]
	cache[cache_id] = ret

	return ret

def getSolutionProgram(secret: str) -> SExp:
	contract = f"(list \"{secret}\")"

	ret = compile_clvm_text(contract, []) # .as_bin().hex()
	return ret

def getSecretFromSolutionProgram(program: str) -> str:
	if program.startswith("0x"):
		program = program[2:]
	s = io.BytesIO(bytes.fromhex(program))
	prg = sexp_from_stream(s, SExp.to)
	ret = prg.first().as_python().decode()
	return ret


def programToPuzzleHash(program: SExp) -> bytes32:
	return sha256tree(program)
