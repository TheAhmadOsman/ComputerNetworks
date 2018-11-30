-- Trivial Routing Protocol dissector
-- Implemented by Roman Yasinovskyy, 2018
-- Declare the protocol
local routing_proto = Proto("trp", "Trivial Routing Protocol")
-- Declare the fields
local TYPES = { [0] = "UPDATE", [1] = "HELLO", [2] = "STATUS REQUEST", [3] = "STATUS RESPONSE" }
local pf_msg_type = ProtoField.new("Message Type", "trp.msg_type", ftypes.UINT8, TYPES)
local pf_src_addr = ProtoField.new("Source", "trp.src_addr", ftypes.IPv4)
local pf_dst_addr = ProtoField.new("Destination", "trp.dst_addr", ftypes.IPv4)
local pf_dst_cost = ProtoField.new("Path cost", "trp.dst_cost", ftypes.UINT8)
local pf_hello_txt = ProtoField.new("Hello text", "trp.hello_txt", ftypes.STRING)
routing_proto.fields = { pf_msg_type, pf_src_addr, pf_dst_addr, pf_dst_cost, pf_hello_txt }

function routing_proto.dissector(buffer, packet, tree)
    packet.cols.protocol = "TRP"

    local msg_type = buffer(0, 1):uint()
    local subtree = tree:add(routing_proto, buffer())
    subtree:add(pf_msg_type, buffer(0, 1))
    idx = 1
    packet_remaining = buffer:reported_length_remaining() - 1
    if msg_type == 0 then
        r = 0
        subtree = subtree:add(buffer(idx, packet_remaining), "Distance Vector")
        while packet_remaining > 0 do
            local record = subtree:add(buffer(idx, 5), "Record " .. r)
            record:add(pf_dst_addr, buffer:range(idx, 4))
            idx = idx + 4
            packet_remaining = packet_remaining - 4
            record:add(pf_dst_cost, buffer(idx, 1))
            idx = idx + 1
            packet_remaining = packet_remaining - 1
            r = r + 1
        end
    elseif msg_type == 1 then
        subtree = subtree:add(buffer(idx, packet_remaining), "Hello Message")
        subtree:add(pf_src_addr, buffer:range(idx, 4))
        idx = idx + 4
        packet_remaining = packet_remaining - 4
        subtree:add(pf_dst_addr, buffer:range(idx, 4))
        idx = idx + 4
        packet_remaining = packet_remaining - 4
        subtree:add(pf_hello_txt, buffer:range(idx, packet_remaining))
        idx = idx + packet_remaining
    elseif msg_type == 2 then
        subtree = subtree:add(buffer(idx, packet_remaining), "Request Source")
        subtree:add(pf_src_addr, buffer:range(idx, 4))
        idx = idx + 4
    elseif msg_type == 3 then
        subtree:add(pf_dst_addr, buffer:range(idx, 4))
        idx = idx + 4
        packet_remaining = packet_remaining - 4
        r = 0
        subtree = subtree:add(buffer(idx, packet_remaining), "Distance Vector")
        while packet_remaining > 0 do
            local record = subtree:add(buffer(idx, 5), "Record " .. r)
            record:add(pf_dst_addr, buffer:range(idx, 4))
            idx = idx + 4
            packet_remaining = packet_remaining - 4
            record:add(pf_dst_cost, buffer(idx, 1))
            idx = idx + 1
            packet_remaining = packet_remaining - 1
            r = r + 1
        end
    end
    return idx
end
-- Load the udp.port table and register our protocol to handle port 4300
udp_table = DissectorTable.get("udp.port")
udp_table:add(4300, routing_proto)
