-- trivial routing protocol dissector
-- declare the protocol
local routing_proto = Proto("trp430", "Trivial Routing Protocol")
local pf_src_addr = ProtoField.new("Source", "trp430.src_addr", ftypes.IPv4)
local pf_dst_addr = ProtoField.new("Destination", "trp430.dst_addr", ftypes.IPv4)
local pf_dst_cost = ProtoField.new("Path cost", "trp430.dst_cost", ftypes.UINT8)
local pf_hello_txt = ProtoField.new("Hello text", "trp430.hello_txt", ftypes.STRING)
routing_proto.fields = { pf_src_addr, pf_dst_addr, pf_dst_cost, pf_hello_txt }
local TYPES = { [0] = "UPDATE", [1] = "HELLO", [2] = "STATUS" }
-- create a function to dissect it
function routing_proto.dissector(buffer, pkt, tree)
    pkt.cols.protocol = "TRP430"

    local msg_type = buffer(0, 1):uint()

    local subtree = tree:add(routing_proto, buffer())
    subtree:add(buffer(0, 1), "Message type: " .. TYPES[msg_type] .. " (" .. msg_type ..")")

    if msg_type == 0 then
        idx = 1
        r = 0
        pkt_remaining = buffer:reported_length_remaining() - 1
        subtree = subtree:add(buffer(idx, pkt_remaining), "Distance Vector")
        while pkt_remaining > 0 do
            local record = subtree:add(buffer(idx, 5), "Record " .. r)
            record:add(pf_dst_addr, buffer:range(idx, 4))
            idx = idx + 4
            pkt_remaining = pkt_remaining - 4
            record:add(pf_dst_cost, buffer(idx, 1))
            idx = idx + 1
            pkt_remaining = pkt_remaining - 1
            r = r + 1
        end
    elseif msg_type == 1 then
        idx = 1
        pkt_remaining = buffer:reported_length_remaining() - 1
        subtree = subtree:add(buffer(idx, pkt_remaining), "Hello Message")
        subtree:add(pf_src_addr, buffer:range(idx, 4))
        idx = idx + 4
        pkt_remaining = pkt_remaining - 4
        subtree:add(pf_dst_addr, buffer:range(idx, 4))
        idx = idx + 4
        pkt_remaining = pkt_remaining - 4
        subtree:add(pf_hello_txt, buffer:range(idx, pkt_remaining))
        idx = idx + pkt_remaining
    end
    return idx
end
-- load the udp.port table
udp_table = DissectorTable.get("udp.port")
-- register our protocol to handle udp port 4300
udp_table:add(4300, routing_proto)
