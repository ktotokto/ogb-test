import interact from 'interactjs'
import { ref, onMounted, onUnmounted, watch, toValue } from 'vue'

export function useGameBoardPan(boardRef, options = {}) {
    const {
        onPanStart,
        onPanMove,
        onPanEnd,
        enabled = true
    } = options

    const isPanning = ref(false)
    const panOffset = ref({ x: 0, y: 0 })
    const zoom = ref(1)
    let interactable = null

    const updateTransform = () => {
        if (boardRef.value) {
            boardRef.value.style.transform = `
        translate(${panOffset.value.x}px, ${panOffset.value.y}px) 
        scale(${zoom.value})
      `
            boardRef.value.style.transformOrigin = '0 0'
        }
    }

    const initPan = () => {
        if (!boardRef.value || !enabled) return

        interactable = interact(boardRef.value)
            .draggable({
                enabled: () => props.enabled,
                allowFrom: '.board-pan-area',
                ignoreFrom: '.game-object, .game-object *, button, input, textarea',
                listeners: {
                    start(event) {
                        if (!event.pointerType || event.originalEvent?.altKey || event.originalEvent?.button === 1) {
                            isPanning.value = true
                            boardRef.value.style.cursor = 'grabbing'
                            onPanStart?.(event, { ...panOffset.value })
                        } else {
                            event.preventDefault()
                            return false
                        }
                    },
                    move(event) {
                        if (!isPanning.value) return

                        panOffset.value.x += event.dx
                        panOffset.value.y += event.dy

                        updateTransform()
                        onPanMove?.(event, { ...panOffset.value })
                    },
                    end(event) {
                        if (!isPanning.value) return

                        isPanning.value = false
                        boardRef.value.style.cursor = 'default'
                        onPanEnd?.(event, { ...panOffset.value })
                    }
                },
                inertia: true,
                modifiers: [
                ]
            })

        interactable.styleCursor(false)
    }

    const zoomIn = (step = 0.1) => {
        zoom.value = Math.min(3, zoom.value + step)
        updateTransform()
    }

    const zoomOut = (step = 0.1) => {
        zoom.value = Math.max(0.25, zoom.value - step)
        updateTransform()
    }

    const resetZoom = () => {
        zoom.value = 1
        panOffset.value = { x: 0, y: 0 }
        updateTransform()
    }

    const setZoom = (value) => {
        zoom.value = Math.max(0.25, Math.min(3, value))
        updateTransform()
    }

    const handleWheel = (event) => {
        if (event.ctrlKey || event.metaKey) {
            event.preventDefault()
            const delta = event.deltaY > 0 ? -0.1 : 0.1
            if (delta > 0) zoomIn(0.1)
            else zoomOut(0.1)
        }
    }

    const handleKeyDown = (event) => {
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return

        const step = event.shiftKey ? 50 : 20

        switch (event.key) {
            case 'ArrowUp':
                panOffset.value.y += step
                updateTransform()
                break
            case 'ArrowDown':
                panOffset.value.y -= step
                updateTransform()
                break
            case 'ArrowLeft':
                panOffset.value.x += step
                updateTransform()
                break
            case 'ArrowRight':
                panOffset.value.x -= step
                updateTransform()
                break
            case '0':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault()
                    resetZoom()
                }
                break
            case '+':
            case '=':
                zoomIn()
                break
            case '-':
            case '_':
                zoomOut()
                break
        }
    }

    onMounted(() => {
        initPan()
        window.addEventListener('wheel', handleWheel, { passive: false })
        window.addEventListener('keydown', handleKeyDown)
    })

    onUnmounted(() => {
        window.removeEventListener('wheel', handleWheel)
        window.removeEventListener('keydown', handleKeyDown)
        if (interactable) {
            interactable.unset()
            interactable = null
        }
    })

    watch(() => toValue(enabled), (newValue) => {
        if (interactable) {
            interactable.draggable({ enabled: newValue })
        }
    })

    return {
        isPanning,
        panOffset,
        zoom,
        zoomIn,
        zoomOut,
        resetZoom,
        setZoom
    }
}