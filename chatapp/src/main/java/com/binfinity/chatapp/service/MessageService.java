package com.binfinity.chatapp.service;

import com.binfinity.chatapp.entity.Message;
import com.binfinity.chatapp.entity.User;
import com.binfinity.chatapp.repository.MessageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MessageService {
    private final MessageRepository messageRepository;
    private final UserService userService;

    // Send message from sender to receiver
    public Message sendMessage(String senderUsername, String receiverUsername, String content) {
        User sender = userService.findByUsername(senderUsername);
        User receiver = userService.findByUsername(receiverUsername);

        // Ensure the sender and receiver are friends
        if (!sender.getFriends().contains(receiver)) {
            throw new IllegalArgumentException("你们还不是朋友，无法发送消息");
        }

        Message message = new Message();
        message.setSender(sender);
        message.setReceiver(receiver);
        message.setContent(content);
        message.setTimestamp(LocalDateTime.now());

        return messageRepository.save(message);
    }

    // 获取单向的聊天记录（发送者到接收者）
    public List<Message> getChatHistory(String senderUsername, String receiverUsername) {
        User sender = userService.findByUsername(senderUsername);
        User receiver = userService.findByUsername(receiverUsername);

        // 获取从发送者到接收者的消息
        List<Message> messagesFromSenderToReceiver = messageRepository.findBySenderAndReceiver(sender, receiver);

        // 排序消息（根据时间戳）
        messagesFromSenderToReceiver.sort((m1, m2) -> m1.getTimestamp().compareTo(m2.getTimestamp()));

        return messagesFromSenderToReceiver;
    }

}
