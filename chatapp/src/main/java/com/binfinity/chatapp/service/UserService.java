package com.binfinity.chatapp.service;

import com.binfinity.chatapp.entity.User;
import com.binfinity.chatapp.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.binfinity.chatapp.config.JwtUtil;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;  // 注入 JwtUtil

    private static final Logger logger = LoggerFactory.getLogger(UserService.class);

    public String login(String username, String password) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("用户不存在"));

        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new BadCredentialsException("密码错误");
        }

        // 生成 JWT 令牌
        return jwtUtil.generateToken(user.getUsername());
    }

        // 获取好友列表
        public List<String> getFriendList(String username) {
            User user = userRepository.findByUsername(username)
                    .orElseThrow(() -> new RuntimeException("用户不存在"));
            // 返回用户名列表
            return user.getFriends().stream().map(User::getUsername).collect(Collectors.toList());
        }


    // Register a new user
    @Transactional
    public User register(String username, String password) {
        logger.info("Registering user: {}", username);
        if (userRepository.findByUsername(username).isPresent()) {
            throw new RuntimeException("用户名已存在");
        }
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        return userRepository.save(user);
    }

    // Find a user by username
    public User findByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("用户不存在"));
    }

    // Add a friend to the user
    @Transactional
    public void addFriend(String username, String friendUsername) {
        if (username.equals(friendUsername)) {
            throw new IllegalArgumentException("不能将自己添加为好友");
        }

        User user = findByUsername(username);
        User friend = findByUsername(friendUsername);

        // Check if they are already friends
        if (user.getFriends().contains(friend)) {
            throw new IllegalArgumentException("已经是好友");
        }

        user.getFriends().add(friend);
        friend.getFriends().add(user);

        userRepository.save(user);
        userRepository.save(friend);
    }
}
