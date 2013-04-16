from random import shuffle

from ..dprint import dprint
from ..debugcommunity import DebugCommunity
from ..debugcommunity import DebugNode
from .dispersytestclass import DispersyTestClass, call_on_dispersy_thread

class TestMissingMessage(DispersyTestClass):
    @call_on_dispersy_thread
    def test_single_request(self):
        """
        SELF generates a few messages and NODE requests one of them.
        """
        community = DebugCommunity.create_community(self._dispersy, self._my_member)

        node = DebugNode()
        node.init_socket()
        node.set_community(community)
        node.init_my_member()

        # create messages
        messages = []
        for i in xrange(10):
            messages.append(community.create_full_sync_text("Message #%d" % i))

        # ensure we don't obtain the messages from the socket cache
        node.drop_packets()

        for message in messages:
            # request messages
            node.give_message(node.create_dispersy_missing_message_message(community.my_member, [message.distribution.global_time], 25, community.my_candidate))
            yield 0.11

            # receive response
            _, response = node.receive_message(message_names=[message.name])
            self.assertEqual(response.distribution.global_time, message.distribution.global_time)
            self.assertEqual(response.payload.text, message.payload.text)
            dprint("ok @", response.distribution.global_time)

        # cleanup
        community.create_dispersy_destroy_community(u"hard-kill")
        self._dispersy.get_community(community.cid).unload_community()

    @call_on_dispersy_thread
    def test_single_request_out_of_order(self):
        """
        SELF generates a few messages and NODE requests one of them.
        """
        community = DebugCommunity.create_community(self._dispersy, self._my_member)

        node = DebugNode()
        node.init_socket()
        node.set_community(community)
        node.init_my_member()

        # create messages
        messages = []
        for i in xrange(10):
            messages.append(community.create_full_sync_text("Message #%d" % i))

        # ensure we don't obtain the messages from the socket cache
        node.drop_packets()

        shuffle(messages)
        for message in messages:
            # request messages
            node.give_message(node.create_dispersy_missing_message_message(community.my_member, [message.distribution.global_time], 25, community.my_candidate))
            yield 0.11

            # receive response
            _, response = node.receive_message(message_names=[message.name])
            self.assertEqual(response.distribution.global_time, message.distribution.global_time)
            self.assertEqual(response.payload.text, message.payload.text)
            dprint("ok @", response.distribution.global_time)

        # cleanup
        community.create_dispersy_destroy_community(u"hard-kill")
        self._dispersy.get_community(community.cid).unload_community()

    @call_on_dispersy_thread
    def test_triple_request(self):
        """
        SELF generates a few messages and NODE requests three of them.
        """
        community = DebugCommunity.create_community(self._dispersy, self._my_member)

        node = DebugNode()
        node.init_socket()
        node.set_community(community)
        node.init_my_member()

        # create messages
        messages = []
        for i in xrange(10):
            messages.append(community.create_full_sync_text("Message #%d" % i))
        meta = messages[0].meta

        # ensure we don't obtain the messages from the socket cache
        node.drop_packets()

        # request messages
        global_times = [messages[index].distribution.global_time for index in [2, 4, 6]]
        node.give_message(node.create_dispersy_missing_message_message(community.my_member, global_times, 25, community.my_candidate))
        yield 0.11

        # receive response
        responses = []
        _, response = node.receive_message(message_names=[meta.name])
        responses.append(response)
        _, response = node.receive_message(message_names=[meta.name])
        responses.append(response)
        _, response = node.receive_message(message_names=[meta.name])
        responses.append(response)

        self.assertEqual(sorted(response.distribution.global_time for response in responses), global_times)
        dprint("ok @", global_times)

        # cleanup
        community.create_dispersy_destroy_community(u"hard-kill")
        self._dispersy.get_community(community.cid).unload_community()
