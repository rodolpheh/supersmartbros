function poll_data()
	data = {}
	-- getting and formatting lives value
	local lives_int = memory.readbyte(0x075a)
	-- death is -1 (255) value, convert to 0 lives for display
	if lives_int == 255 then
		lives_int = 0
	else
		lives_int = lives_int + 1
	end
	local lives = string.format(
		"LIVES: %02d\n",
		lives_int
	)

	-- getting and formatting coins value
	local coins = string.format(
		"COINS: %02d\n",
		memory.readbyte(0x075e)
	)

	-- getting and formatting world-level value
	local world = memory.readbyte(0x075f) + 1
	local level = memory.readbyte(0x0760) + 1

	-- weird, only the [1-2 ; 1-4] level have an offset of one
	if (world == 1 and level >= 2) then level = level - 1 end
	local world_level = string.format(
		"WORLD: %d-%d\n",
		world,
		level
	)

	local score = {}
	local startAddress = 0x07dd
	for i =0,5 do
		local byteRead = memory.readbyte(startAddress+i)
		score[#score+1] = tostring(byteRead)
	end
	score[#score+1] = "0"

	local status = memory.readbyte(0x0756)
	if status == 0 then
		status = "SMOL"
	elseif status == 1 then
		status = "BIGG"
	else
		status = "FAYA"
	end

	score = table.concat(score)
	data[0] = lives
	data[1] = coins
	data[2] = world_level
	data[3] = string.format("SCORE: %s\n", score)
	data[4] = string.format("STATUS: %s\n", status)

	return data
end

file = io.open("test.txt", "w")

function dump_data(data)
	local world_level = data[2]
	local lives = data[0]
	local coins = data[1]
	local score = data[3]
	local status = data[4]

	-- Rewinding file to beginning
	file:seek("set", 0);
	file:write(world_level)
	file:write(lives)
	file:write(coins)
	file:write(score)
	file:write(status)
end

while (true) do
	dump_data(poll_data())
	FCEU.frameadvance()
end

file:close()

