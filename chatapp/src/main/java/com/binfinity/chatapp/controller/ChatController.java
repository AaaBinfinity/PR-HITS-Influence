package com.binfinity.chatapp.controller;

import com.binfinity.chatapp.entity.Message;
import com.binfinity.chatapp.service.MessageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@CrossOrigin(origins = "*") // 允许所有来源访问
@RestController
@RequestMapping("/chat")
@RequiredArgsConstructor
public class ChatController {
    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);
    private final MessageService messageService;

    // 获取两个用户之间的聊天记录（单向）
    @GetMapping("/history")
    public ResponseEntity<?> getChatHistory(@RequestParam String senderUsername, @RequestParam String receiverUsername) {
        logger.info("获取聊天记录请求：发送者={}, 接收者={}", senderUsername, receiverUsername);
        try {
            // 调用服务层获取历史聊天记录
            List<Message> chatHistory = messageService.getChatHistory(senderUsername, receiverUsername);

            // 记录成功
            logger.info("聊天记录获取成功：发送者={}, 接收者={}, 记录数={}", senderUsername, receiverUsername, chatHistory.size());

            // 返回成功响应，包含历史消息
            return ResponseEntity.ok(chatHistory);
        } catch (Exception e) {
            // 记录异常
            logger.error("获取聊天记录失败：发送者={}, 接收者={}, 错误信息={}", senderUsername, receiverUsername, e.getMessage(), e);
            // 捕获异常并返回错误信息
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/send")
    public ResponseEntity<?> sendMessage(@RequestBody Map<String, String> request) {
        String sender = request.get("sender");
        String receiver = request.get("receiver");
        String content = request.get("content");

        logger.info("发送消息请求：发送者={}, 接收者={}, 内容={}", sender, receiver, content);

        try {
            // 调用服务层发送消息
            Message message = messageService.sendMessage(sender, receiver, content);

            // 记录成功
            logger.info("消息发送成功：发送者={}, 接收者={}, 内容={}, 时间戳={}", sender, receiver, message.getContent(), message.getTimestamp());

            // 返回成功响应
            return ResponseEntity.ok(Map.of("message", "消息发送成功", "content", message.getContent(), "timestamp", message.getTimestamp()));
        } catch (Exception e) {
            // 记录异常
            logger.error("发送消息失败：发送者={}, 接收者={}, 错误信息={}", sender, receiver, e.getMessage(), e);
            // 捕获异常并返回错误信息
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", e.getMessage()));
        }
    }
}
