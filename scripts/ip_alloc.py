def addr_to_str(ip):
    return "{}.{}.{}.{}".format(
        ip >> 24, (ip >> 16) & 0xFF, (ip >> 8) & 0xFF, ip & 0xFF
    )


class IPAllocator:
    def __init__(self):
        self.base = 3232266241  # (192 << 24) + (168 << 16) + (120 << 8) + 1
        self.netmask = 0xFFFF0000  # 255.255.0.0
        self.assigned = 1  # reserve one for gateway
        pass

    def get_base(self):
        return self.base

    def get_netmask(self):
        return self.netmask

    def next(self):
        nxt = self.base + self.assigned
        self.assigned += 1
        # check for overflow out of our subnet mask
        assert (nxt & ~self.netmask) > (self.base & ~self.netmask), (
            f"{addr_to_str(nxt)} overflows"
        )
        return nxt

    def cur(self):
        return self.base + self.assigned
