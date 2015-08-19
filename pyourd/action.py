def push_device(container, device_id, notification):
    return push_devices(container, [device_id], notification)


def push_devices(container, device_ids, notification):
    params = {
            'device_ids': device_ids,
            'notification': notification,
            }
    return container.send_action('push:device', params)


def push_user(container, user_id, notification):
    return push_users(container, [user_id], notification)


def push_users(container, user_ids, notification):
    params = {
            'user_ids': user_ids,
            'notification': notification,
            }
    return container.send_action('push:user', params)
